#!/usr/bin/env python3
"""
analyze-subtitles-ai.py - 使用 AI 分析字幕生成结构化总结
基于阿里云 DashScope API (qwen3.5-plus)

用法：python3 analyze-subtitles-ai.py <字幕文件> <元数据文件> <输出文件>
"""

import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime

# 读取环境变量
from dotenv import load_dotenv
load_dotenv(Path.home() / '.openclaw' / '.env')

DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')

if not DASHSCOPE_API_KEY:
    print("❌ 错误：缺少 DASHSCOPE_API_KEY，请检查 ~/.openclaw/.env")
    sys.exit(1)

# 使用 HTTP 直接调用（避免 OpenAI SDK 超时问题）
import requests
DASHSCOPE_BASE_URL = os.getenv('DASHSCOPE_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
# 模型选择：qwen3.5-plus（高质量）或 qwen-turbo（快速）
MODEL = os.getenv('DASHSCOPE_MODEL', 'qwen3.5-plus')


def time_to_seconds(time_str: str) -> int:
    """
    将时间戳字符串转换为秒数（用于排序）
    支持格式：MM:SS 或 HH:MM:SS
    """
    if not time_str:
        return 0
    parts = time_str.replace('[', '').replace(']', '').split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0


def parse_vtt(vtt_file):
    """解析 VTT 字幕文件，返回带时间戳的字幕列表"""
    subtitles = []
    
    with open(vtt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除 WEBVTT 头部
    content = re.sub(r'^WEBVTT.*?\n\n', '', content, flags=re.DOTALL)
    
    # 解析每个字幕块（支持两种格式：HH:MM:SS 和 MM:SS）
    pattern = r'(\d{1,2}:\d{2}:\d{2}\.\d{3}|\d{1,2}:\d{2}\.\d{3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}\.\d{3}|\d{1,2}:\d{2}\.\d{3})\n(.*?)(?=\n\n|\n*$)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for start, end, text in matches:
        # 清理文本
        text = re.sub(r'<[^>]+>', '', text)  # 移除 HTML 标签
        text = re.sub(r'\s+', ' ', text).strip()
        
        if text:
            subtitles.append({
                'start': start,
                'end': end,
                'text': text
            })
    
    return subtitles


def extract_transcript_text(subtitles):
    """提取纯文本用于 AI 分析"""
    return '\n'.join([sub['text'] for sub in subtitles])


def load_params() -> dict:
    """加载 AI 分析参数配置"""
    params_path = os.path.join(os.path.dirname(__file__), '..', 'prompt.json')
    try:
        with open(params_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"   ⚠️  参数文件不存在：{params_path}，使用默认配置")
        return {
            "system_prompt": "你是一个专业的视频内容分析专家，擅长从视频字幕中提取关键信息并生成结构化总结。",
            "user_prompt_template": "你是一个专业的视频内容分析专家。请分析以下视频字幕内容，生成结构化的总结。\n\n## 视频信息\n- 标题：{title}\n- UP 主：{uploader}\n- 时长：{duration}\n\n## 字幕内容\n{transcript}\n\n## 任务要求\n\n请按照以下 JSON 格式输出分析结果：\n\n```json\n{{\n  \"note\": \"100-200 字概述\",\n  \"key_points\": [\n    {{\"emoji\": \"🎯\", \"title\": \"要点标题\", \"description\": \"详细描述\", \"time\": \"MM:SS\"}}\n  ],\n  \"concepts\": [\n    {{\"term\": \"概念名\", \"definition\": \"解释\", \"time\": \"MM:SS\"}}\n  ],\n  \"warnings\": [\n    {{\"text\": \"注意事项内容\", \"time\": \"MM:SS\"}}\n  ],\n  \"summary\": \"最终归纳段落，200-300 字\"\n}}\n```\n\n## 输出要求\n\n1. **note**: 150-250 字\n2. **key_points**: 5-8 个核心要点\n3. **concepts**: 3-5 个关键概念\n4. **warnings**: 2-4 个注意事项\n5. **summary**: 200-300 字最终总结\n\n现在请开始分析：",
            "output_constraints": {
                "max_note_chars": 250,
                "min_key_points": 5,
                "max_key_points": 8,
                "min_concepts": 3,
                "max_concepts": 5,
                "min_warnings": 2,
                "max_warnings": 4,
                "max_summary_chars": 300
            }
        }


def ai_analyze(transcript: str, video_info: dict) -> dict:
    """
    使用 AI 分析字幕内容，返回模板所需的数据结构
    
    Returns:
        dict: 直接匹配模板变量的数据结构
    """
    
    # 加载参数配置
    params = load_params()
    system_prompt = params.get('system_prompt', '你是一个专业的视频内容分析专家。')
    prompt_template = params.get('user_prompt_template', '')
    
    # 构建提示词
    prompt = prompt_template.format(
        title=video_info.get('title', 'Unknown'),
        uploader=video_info.get('uploader', 'Unknown'),
        duration=video_info.get('duration_string', 'Unknown'),
        transcript=transcript[:15000]  # 限制字幕长度
    )

    try:
        print(f"   🤖 调用 AI 分析 (模型：{MODEL})...")
        
        word_count = len(transcript.split())
        MAX_WORDS = 12000
        
        if word_count > MAX_WORDS:
            print(f"   ⚠️  字幕过长 ({word_count}字)，截断到 {MAX_WORDS}字")
            part_size = MAX_WORDS // 2
            transcript = transcript[:part_size] + "\n...[内容过长，已截断]...\n" + transcript[-part_size:]
        
        headers = {
            'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': MODEL,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ],
            'stream': False
        }
        
        # 超时重试机制（超时：300s → 600s → 900s）
        response = None
        for attempt in range(3):
            try:
                timeout = [300, 600, 900][attempt]
                print(f"   尝试 {attempt + 1}/3 (超时：{timeout}s)...")
                response = requests.post(
                    f'{DASHSCOPE_BASE_URL}/chat/completions',
                    headers=headers,
                    json=data,
                    timeout=timeout
                )
                if response.status_code == 200:
                    break
            except requests.exceptions.Timeout:
                print(f"   ⚠️  超时，准备重试...")
                if attempt == 2:
                    raise
        
        if response.status_code == 200:
            ai_response = response.json()['choices'][0]['message']['content']
            
            # 提取 JSON 内容
            json_match = re.search(r'```json\s*(.*?)\s*```', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = ai_response
            
            result = json.loads(json_str)
            print(f"   ✅ AI 分析完成")
            return result
        else:
            print(f"   ❌ AI 调用失败：{response.status_code} - {response.text[:200]}")
            return None
    
    except Exception as e:
        print(f"   ❌ 分析异常：{str(e)}")
        return None


def load_screenshot_urls(urls_file: str) -> list:
    """加载截图 URL 列表"""
    urls = []
    if os.path.exists(urls_file):
        try:
            with open(urls_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    if item.get('success') and item.get('oss_url'):
                        urls.append(item['oss_url'])
        except:
            pass
    return urls


def load_template() -> str:
    """加载 Markdown 模板"""
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'summary.md')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"   ❌ 模板文件不存在：{template_path}")
        sys.exit(1)


def format_tags(tags: list) -> str:
    """格式化标签为模板格式：`标签 1` `标签 2` `标签 3` `标签 4` `标签 5`"""
    # 确保正好 5 个标签
    default_tags = ["视频总结", "AI 分析", "教程", "技巧", "知识分享"]
    while len(tags) < 5:
        for t in default_tags:
            if t not in tags:
                tags.append(t)
                if len(tags) >= 5:
                    break
    tags = tags[:5]
    return ' '.join([f"`{tag}`" for tag in tags])


def format_key_points(key_points: list) -> str:
    """
    格式化核心要点为模板格式（无截图）：
    **{emoji} {要点标题}**
    {详细描述} `[{时间戳}]`
    """
    if not key_points:
        return "*AI 分析中*"
    
    # 按时间戳排序
    sorted_points = sorted(key_points, key=lambda x: time_to_seconds(x.get('time', '00:00')))
    
    lines = []
    for point in sorted_points:
        emoji = point.get('emoji', '🎯')
        title = point.get('title', '要点')
        description = point.get('description', '')
        time = point.get('time', '00:00')
        
        lines.append(f"**{emoji} {title}**")
        lines.append(f"{description} `[{time}]`")
        lines.append("")  # 每个要点后空行分隔
    
    return '\n'.join(lines)


def format_video_chapters(chapters: list, screenshot_urls: list = None, cover_url: str = None) -> str:
    """
    格式化视频章节为模板格式：
    **{emoji} {章节标题}** `[{时间戳}]`
    ![章节截图]({截图 URL})
    
    Args:
        chapters: 视频章节列表，每个包含 emoji, title, time
        screenshot_urls: 截图 URL 列表
        cover_url: 封面图 URL（当截图不存在时用作占位符）
    """
    if not chapters:
        return "*AI 分析中*"
    
    # 按时间戳排序
    sorted_chapters = sorted(chapters, key=lambda x: time_to_seconds(x.get('time', '00:00')))
    
    lines = []
    for i, chapter in enumerate(sorted_chapters):
        emoji = chapter.get('emoji', '🎬')
        title = chapter.get('title', '章节')
        time = chapter.get('time', '00:00')
        
        lines.append(f"**{emoji} {title}** `[{time}]`")
        
        # 插入对应的截图（如果有）- 紧跟标题
        if screenshot_urls and i < len(screenshot_urls):
            lines.append(f"![章节截图]({screenshot_urls[i]})")
        elif cover_url:
            # 没有截图时使用封面图作为占位符
            lines.append(f"![章节截图]({cover_url})")
        
        lines.append("")  # 每个章节后空行分隔
    
    return '\n'.join(lines)


def format_warnings(warnings: list) -> str:
    """
    格式化注意事项为模板格式（无截图）：
    - {注意事项内容} `[{时间戳}]`
    """
    if not warnings:
        return "*AI 分析中*"
    
    # 按时间戳排序
    sorted_warnings = sorted(warnings, key=lambda x: time_to_seconds(x.get('time', '00:00')))
    
    lines = []
    for warning in sorted_warnings:
        text = warning.get('text', '')
        time = warning.get('time', '')
        lines.append(f"- {text} `[{time}]`")
        lines.append("")  # 每条注意事项后空行分隔
    
    return '\n'.join(lines)


def format_concepts(concepts: list) -> str:
    """
    格式化关键概念为模板格式（2 列表格）：
    | 概念 | 解释 |
    |------|------|
    | **{概念名}** | {解释} `[{时间戳}]` |
    
    按时间戳升序排序（时间早的靠前）
    """
    if not concepts:
        return "*AI 分析中*"
    
    # 按时间戳排序
    sorted_concepts = sorted(concepts, key=lambda x: time_to_seconds(x.get('time', '00:00')))
    
    lines = []
    lines.append("| 概念 | 解释 |")
    lines.append("| :--- | :--- |")
    
    for c in sorted_concepts:
        term = c.get('term', '')
        definition = c.get('definition', '')
        time = c.get('time', '')
        lines.append(f"| **{term}** | {definition} `[{time}]` |")
    
    return '\n'.join(lines)


def format_screenshots(screenshot_urls: list, screenshot_times: list) -> str:
    """
    格式化视频帧截图为模板格式：
    **截图 N [{时间}]**
    ![截图 N]({截图 URL})
    > {截图内容说明}
    """
    if not screenshot_urls:
        return "*AI 分析中*"
    
    lines = []
    for i, (url, time_str) in enumerate(zip(screenshot_urls, screenshot_times), 1):
        lines.append(f"**截图 {i} [{time_str}]**")
        lines.append(f"![截图 {i}]({url})")
        lines.append("> 视频关键帧展示")
        lines.append("")  # 空行分隔
    
    return '\n'.join(lines)


def calculate_screenshot_times(duration_str: str, num_screenshots: int) -> list:
    """根据视频时长计算截图时间戳"""
    # 解析视频时长（秒）
    duration_parts = duration_str.split(':')
    if len(duration_parts) == 2:
        total_seconds = int(duration_parts[0]) * 60 + int(duration_parts[1])
    elif len(duration_parts) == 3:
        total_seconds = int(duration_parts[0]) * 3600 + int(duration_parts[1]) * 60 + int(duration_parts[2])
    else:
        total_seconds = 0
    
    screenshot_times = []
    if num_screenshots > 1 and total_seconds > 0:
        interval = total_seconds / (num_screenshots + 1)
        for i in range(num_screenshots):
            sec = int(interval * (i + 1))
            mins, secs = divmod(sec, 60)
            screenshot_times.append(f"{mins:02d}:{secs:02d}")
    else:
        screenshot_times = ["00:00"] * num_screenshots
    
    return screenshot_times


def load_screenshot_times(output_dir: str) -> list:
    """加载截图时间戳列表"""
    times_file = os.path.join(output_dir, 'screenshot_times.txt')
    times = []
    if os.path.exists(times_file):
        try:
            with open(times_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        times.append(line)
        except:
            pass
    return times


def generate_markdown(video_info: dict, ai_result: dict, screenshot_urls: list, screenshot_times: list = None) -> str:
    """
    使用模板生成 Markdown 格式的总结
    
    数据与模板分离：此函数只负责数据格式转换，不修改模板内容
    
    Args:
        screenshot_times: 截图时间戳列表（从 screenshot_times.txt 读取），如果为 None 则自动计算
    """
    
    # 提取视频元数据
    title = video_info.get('title', 'Unknown')
    uploader = video_info.get('uploader', 'Unknown')
    duration = video_info.get('duration_string', 'Unknown')
    view_count = video_info.get('view_count', 0)
    like_count = video_info.get('like_count', 0)
    comment_count = video_info.get('comment_count', 0)
    thumbnail = video_info.get('thumbnail', '')
    webpage_url = video_info.get('webpage_url', '')
    upload_date = video_info.get('upload_date', '')
    
    # 从 URL 提取视频来源平台
    source = "Unknown"
    if webpage_url:
        if "bilibili.com" in webpage_url or "b23.tv" in webpage_url:
            source = "Bilibili"
        elif "xiaohongshu.com" in webpage_url:
            source = "小红书"
        elif "douyin.com" in webpage_url:
            source = "抖音"
        elif "youtube.com" in webpage_url or "youtu.be" in webpage_url:
            source = "YouTube"
        elif "channels.weixin.qq.com" in webpage_url:
            source = "微信视频"
    
    # 格式化日期（处理时间戳和字符串两种格式）
    if upload_date:
        if isinstance(upload_date, int):
            # 时间戳格式（秒）- 如 B 站 API 的 pubdate
            try:
                ts = int(upload_date)
                if ts > 10000000000:  # 毫秒时间戳
                    ts = ts // 1000
                publish_date = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
            except:
                publish_date = datetime.now().strftime("%Y-%m-%d")
        elif isinstance(upload_date, str) and upload_date.isdigit() and len(upload_date) >= 8:
            # 字符串格式 YYYYMMDD - 如 yt-dlp 的 upload_date
            publish_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
        else:
            publish_date = datetime.now().strftime("%Y-%m-%d")
    else:
        publish_date = datetime.now().strftime("%Y-%m-%d")
    
    # 构建标签（完全使用视频原始标签，尊重作者定义）
    # 1. 从元数据提取原始标签
    video_tags = video_info.get('tags', [])
    
    # 2. 筛选高质量标签（去除过长/过短，保留 2-6 字符）
    filtered_tags = [t for t in video_tags if 2 <= len(t) <= 6]
    
    # 3. 去重并限制数量（最多 5 个）
    seen = set()
    unique_tags = []
    for t in filtered_tags:
        if t.lower() not in seen:
            seen.add(t.lower())
            unique_tags.append(t)
            if len(unique_tags) >= 5:
                break
    
    # 4. 不足 5 个时用默认值补齐
    default_tags = ["视频总结", "AI 分析", "教程", "技巧", "知识分享"]
    while len(unique_tags) < 5:
        for t in default_tags:
            if t not in unique_tags:
                unique_tags.append(t)
                if len(unique_tags) >= 5:
                    break
    
    tags = unique_tags[:5]  # 确保正好 5 个
    
    # 格式化各个模块
    tags_md = format_tags(tags)
    
    # 计算截图时间戳（优先使用保存的时间戳）
    if screenshot_times is None:
        screenshot_times = calculate_screenshot_times(duration, len(screenshot_urls))
    
    # 构建视频章节（从核心要点提取章节信息，用于视频章节展示）
    video_chapters = []
    if ai_result:
        for point in ai_result.get('key_points', []):
            video_chapters.append({
                'emoji': point.get('emoji', '🎬'),
                'title': point.get('title', '章节'),
                'time': point.get('time', '00:00')
            })
    
    # 分配截图 URL：全部给视频章节
    video_chapter_urls = screenshot_urls if screenshot_urls else []
    
    # 格式化各个模块（核心要点和注意事项不再需要截图）
    key_points_md = format_key_points(ai_result.get('key_points', []) if ai_result else [])
    video_chapters_md = format_video_chapters(video_chapters, video_chapter_urls, thumbnail)
    warnings_md = format_warnings(ai_result.get('warnings', []) if ai_result else [])
    concepts_md = format_concepts(ai_result.get('concepts', []) if ai_result else [])
    
    # 准备模板变量字典（键名必须与模板中的占位符完全一致）
    format_dict = {
        '视频标题': title,
        '标签 1': tags[0] if len(tags) > 0 else '视频总结',
        '标签 2': tags[1] if len(tags) > 1 else 'AI 分析',
        '标签 3': tags[2] if len(tags) > 2 else '教程',
        '标签 4': tags[3] if len(tags) > 3 else '技巧',
        '标签 5': tags[4] if len(tags) > 4 else '知识分享',
        'UP 主名称': uploader,
        '封面 URL': thumbnail,
        '视频来源': source,
        '100-200 字概述': ai_result.get('note', '*AI 生成失败*') if ai_result else '*AI 生成失败*',
        '视频 URL': webpage_url,
        '视频时长': duration,  # 修复：模板中是{视频时长}不是{时长}
        '时长': duration,  # 保留兼容
        '发布日期': publish_date,
        '播放量': f"{view_count:,}" if view_count else "0",
        '点赞数': f"{like_count:,}" if like_count else "0",
        '评论数': f"{comment_count:,}" if comment_count else "0",
        '最终归纳段落': ai_result.get('summary', '*AI 生成失败*') if ai_result else '*AI 生成失败*',
        '生成日期': datetime.now().strftime("%Y-%m-%d"),
    }
    
    # 加载模板
    template = load_template()
    
    # 使用自定义方式替换模板变量
    # 因为模板中有重复的占位符（如多个{emoji} {要点标题}），需要特殊处理
    md = template
    
    # 先替换唯一的变量
    for key, value in format_dict.items():
        md = md.replace('{' + key + '}', str(value))
    
    # 替换核心要点部分（整个区块替换）
    key_points_pattern = r'## 🎯 核心要点\n\n(.*?)\n\n---'
    key_points_replacement = f"## 🎯 核心要点\n\n{key_points_md}\n\n---"
    md = re.sub(key_points_pattern, key_points_replacement, md, flags=re.DOTALL)
    
    # 替换视频章节部分
    video_chapters_pattern = r'## 🎬 视频章节\n\n(.*?)\n\n---'
    video_chapters_replacement = f"## 🎬 视频章节\n\n{video_chapters_md}\n\n---"
    md = re.sub(video_chapters_pattern, video_chapters_replacement, md, flags=re.DOTALL)
    
    # 替换注意事项部分
    warnings_pattern = r'## ⚠️ 注意事项\n\n(.*?)\n\n---'
    warnings_replacement = f"## ⚠️ 注意事项\n\n{warnings_md}\n\n---"
    md = re.sub(warnings_pattern, warnings_replacement, md, flags=re.DOTALL)
    
    # 替换关键概念部分
    concepts_pattern = r'## 📚 关键概念\n\n(.*?)\n\n---'
    concepts_replacement = f"## 📚 关键概念\n\n{concepts_md}\n\n---"
    md = re.sub(concepts_pattern, concepts_replacement, md, flags=re.DOTALL)
    
    # 移除旧的视频帧截图章节（如果存在）
    screenshots_pattern = r'## 🎬 视频帧截图\n\n(.*?)\n\n---'
    md = re.sub(screenshots_pattern, '', md, flags=re.DOTALL)
    
    return md


def main():
    if len(sys.argv) < 4:
        print("用法：python3 analyze-subtitles-ai.py <字幕文件> <元数据文件> <输出文件>")
        sys.exit(1)
    
    vtt_file = sys.argv[1]
    meta_file = sys.argv[2]
    output_file = sys.argv[3]
    
    print("=" * 50)
    print("🧠 AI 字幕分析器 v0.1.2")
    print("=" * 50)
    print()
    
    output_dir = os.path.dirname(output_file)
    ai_json_file = os.path.join(output_dir, 'ai_result.json')
    
    # 检查是否已有 AI 结果（第二次调用，只渲染 Markdown）
    if os.path.exists(ai_json_file):
        print(f"📊 加载已有 AI 结果：{ai_json_file}")
        with open(ai_json_file, 'r', encoding='utf-8') as f:
            ai_result = json.load(f)
        
        print(f"📊 加载元数据：{meta_file}")
        with open(meta_file, 'r', encoding='utf-8') as f:
            video_info = json.load(f)
        print(f"   视频：{video_info.get('title', 'Unknown')}")
        print()
        
        # 加载截图 URL
        screenshot_urls = load_screenshot_urls(os.path.join(output_dir, 'screenshot_urls.txt'))
        print(f"   📸 加载截图链接：{len(screenshot_urls)} 张")
        
        # 加载截图时间戳（从 screenshot_times.txt 读取）
        screenshot_times = load_screenshot_times(output_dir)
        if screenshot_times:
            print(f"   🕐 加载截图时间戳：{len(screenshot_times)} 个")
        
        # 生成 Markdown
        print("📝 生成结构化总结...")
        md_content = generate_markdown(video_info, ai_result, screenshot_urls, screenshot_times)
        
        # 保存文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✅ 总结生成完成：{output_file}")
        print()
        print("=" * 50)
        print("✨ Markdown 渲染完成！")
        print("=" * 50)
        return
    
    # 第一次调用：执行完整 AI 分析
    # 解析字幕
    print(f"📝 解析字幕：{vtt_file}")
    subtitles = parse_vtt(vtt_file)
    print(f"   找到 {len(subtitles)} 条字幕")
    
    # 提取纯文本
    transcript = extract_transcript_text(subtitles)
    word_count = len(transcript.split())
    print(f"   文本长度：{word_count} 字")
    print()
    
    # 加载元数据
    print(f"📊 加载元数据：{meta_file}")
    with open(meta_file, 'r', encoding='utf-8') as f:
        video_info = json.load(f)
    print(f"   视频：{video_info.get('title', 'Unknown')}")
    print()
    
    # AI 分析
    print("🤖 AI 智能分析...")
    ai_result = ai_analyze(transcript, video_info)
    
    if not ai_result:
        print("   ⚠️  AI 分析失败，使用基础版本")
        md_content = f"""# {video_info.get('title', 'Unknown')}

**Tags:** `视频总结` `AI 分析` `教程` `技巧` `知识分享`

**Status:** ⚠️ AI 分析失败

**Author:** {video_info.get('uploader', 'Unknown')}

**Cover:**
![视频封面]({video_info.get('thumbnail', '')})

---

## 📝 Note

AI 分析暂时不可用，请稍后重试。

---

## 📺 视频信息

**链接:** {video_info.get('webpage_url', '')}
**时长:** {video_info.get('duration_string', 'Unknown')}
**发布:** {datetime.now().strftime("%Y-%m-%d")}
**播放:** 0+ | **点赞:** 0 | **评论:** 0

---

## 🎯 核心要点

*AI 分析失败，无法提取要点*

---

## ⚠️ 注意事项

- *AI 分析失败，无法提取注意事项*

---

## 📚 关键概念

| 概念 | 解释 |
|------|------|
| *AI 分析失败* | *无法提取概念* |

---

## 🎬 视频帧截图

*AI 分析失败，无法生成截图*

---

## 💡 总结

*AI 分析失败，无法生成总结*

---

*生成时间：{datetime.now().strftime("%Y-%m-%d")}*
*技能版本：video-summarizer v1.0.0*
"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"✅ 基础版本已生成：{output_file}")
        return
    
    print()
    
    # 保存 AI 分析结果为 JSON（供截图步骤使用）
    output_dir = os.path.dirname(output_file)
    ai_json_file = os.path.join(output_dir, 'ai_result.json')
    try:
        with open(ai_json_file, 'w', encoding='utf-8') as f:
            json.dump(ai_result, f, ensure_ascii=False, indent=2)
        print(f"   💾 AI 结果已保存：{ai_json_file}")
    except Exception as e:
        print(f"   ⚠️  保存 AI JSON 失败：{e}")
    
    # 加载截图 URL（此时截图已完成，供 Markdown 渲染使用）
    screenshots_dir = os.path.dirname(vtt_file)
    screenshot_urls = load_screenshot_urls(os.path.join(screenshots_dir, 'screenshot_urls.txt'))
    print(f"   📸 加载截图链接：{len(screenshot_urls)} 张")
    
    # 加载截图时间戳（从 screenshot_times.txt 读取）
    screenshot_times = load_screenshot_times(output_dir)
    if screenshot_times:
        print(f"   🕐 加载截图时间戳：{len(screenshot_times)} 个")
    
    # 生成 Markdown
    print("📝 生成结构化总结...")
    md_content = generate_markdown(video_info, ai_result, screenshot_urls, screenshot_times)
    
    # 保存文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"✅ 总结生成完成：{output_file}")
    print()
    print("=" * 50)
    print("✨ AI 分析完成！")
    print("=" * 50)


if __name__ == '__main__':
    main()
