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
from http import HTTPStatus

# 读取环境变量
from dotenv import load_dotenv
load_dotenv(Path.home() / '.openclaw' / '.env')

DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')

if not DASHSCOPE_API_KEY:
    print("❌ 错误：缺少 DASHSCOPE_API_KEY，请检查 ~/.openclaw/.env")
    sys.exit(1)

# 使用 HTTP 直接调用（避免 OpenAI SDK 超时问题）
import requests
DASHSCOPE_BASE_URL = os.getenv('DASHSCOPE_BASE_URL', 'https://coding.dashscope.aliyuncs.com/v1')
MODEL = 'qwen3.5-plus'


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


def ai_analyze(transcript: str, video_info: dict) -> dict:
    """
    使用 AI 分析字幕内容
    
    Returns:
        dict: {
            'note': str,  # 100-200 字概述
            'key_points': list,  # 核心要点 [{time, text}]
            'concepts': list,  # 关键概念 [{term, definition, time}]
            'warnings': list,  # 注意事项
            'summary': str  # 最终总结
        }
    """
    
    # 构建提示词
    prompt = f"""你是一个专业的视频内容分析专家。请分析以下视频字幕内容，生成结构化的总结。

## 视频信息
- 标题：{video_info.get('title', 'Unknown')}
- UP 主：{video_info.get('uploader', 'Unknown')}
- 时长：{video_info.get('duration_string', 'Unknown')}

## 字幕内容
{transcript[:15000]}  # 限制长度，避免超出 token 限制

## 任务要求

请按照以下格式输出分析结果（使用 JSON 格式）：

```json
{{
  "note": "用 100-200 字概括视频的核心内容，说明这个视频讲了什么，适合什么人观看，有什么价值",
  
  "key_points": [
    {{"time": "00:01:23", "text": "核心要点 1 的完整描述"}},
    {{"time": "00:03:45", "text": "核心要点 2 的完整描述"}},
    {{"time": "00:05:12", "text": "核心要点 3 的完整描述"}}
  ],
  
  "concepts": [
    {{"term": "专业术语 1", "definition": "简明解释", "time": "00:02:30"}},
    {{"term": "专业术语 2", "definition": "简明解释", "time": "00:04:15"}}
  ],
  
  "warnings": [
    "需要注意的事项 1",
    "需要注意的事项 2",
    "常见的误区或易错点"
  ],
  
  "summary": "200-300 字的最终总结，包括视频的核心价值、适用场景、学习建议等"
}}
```

## 输出要求

1. **note**: 100-200 字，简洁明了，突出核心价值
2. **key_points**: 3-7 个核心要点，每个要点必须包含时间戳和完整描述
3. **concepts**: 0-5 个关键概念，包含术语、解释、首次出现时间
4. **warnings**: 0-5 个注意事项，包括易错点、前提条件等
5. **summary**: 200-300 字，全面总结视频内容

## 注意事项

- 时间戳格式：HH:MM:SS 或 MM:SS
- 所有描述使用中文
- 保持专业但易懂的风格
- 如果某些内容不存在，对应字段可以是空数组或空字符串

现在请开始分析："""

    try:
        print(f"   🤖 调用 AI 分析 (模型：{MODEL})...")
        
        headers = {
            'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': MODEL,
            'messages': [
                {'role': 'system', 'content': '你是一个专业的视频内容分析专家，擅长从视频字幕中提取关键信息并生成结构化总结。'},
                {'role': 'user', 'content': prompt}
            ],
            'stream': False
        }
        
        response = requests.post(
            f'{DASHSCOPE_BASE_URL}/chat/completions',
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            ai_response = response.json()['choices'][0]['message']['content']
            
            # 提取 JSON 内容
            json_match = re.search(r'```json\s*(.*?)\s*```', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 尝试直接解析
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


def generate_markdown(video_info: dict, ai_result: dict, screenshots_md: str = "") -> str:
    """生成 Markdown 格式的总结"""
    
    title = video_info.get('title', 'Unknown')
    uploader = video_info.get('uploader', 'Unknown')
    duration = video_info.get('duration_string', 'Unknown')
    view_count = video_info.get('view_count', 0)
    like_count = video_info.get('like_count', 0)
    thumbnail = video_info.get('thumbnail', '')
    webpage_url = video_info.get('webpage_url', '')
    
    # 构建 Tags
    tags = ["视频总结", "AI 分析"]
    if '教程' in title or '教程' in ai_result.get('note', ''):
        tags.append("教程")
    if '技巧' in title or '方法' in ai_result.get('note', ''):
        tags.append("技巧")
    
    tags_md = ' '.join([f"`{tag}`" for tag in tags])
    
    # 核心要点
    key_points_md = ""
    if ai_result.get('key_points'):
        for i, point in enumerate(ai_result['key_points'], 1):
            time = point.get('time', '00:00')
            text = point.get('text', '')
            key_points_md += f"**要点 {i}** `[{time}]`\n"
            key_points_md += f"{text}\n\n"
    
    # 关键概念
    concepts_md = ""
    if ai_result.get('concepts'):
        concepts_md = "## 📚 关键概念\n\n"
        concepts_md += "| 概念 | 解释 | 时间 |\n"
        concepts_md += "|------|------|------|\n"
        for c in ai_result['concepts']:
            term = c.get('term', '')
            definition = c.get('definition', '')
            time = c.get('time', '')
            concepts_md += f"| **{term}** | {definition} | `{time}` |\n"
        concepts_md += "\n---\n\n"
    
    # 注意事项
    warnings_md = ""
    if ai_result.get('warnings'):
        warnings_md = "## ⚠️ 注意事项\n\n"
        for i, warning in enumerate(ai_result['warnings'], 1):
            warnings_md += f"{i}. {warning}\n"
        warnings_md += "\n---\n\n"
    
    # 视频帧截图
    screenshots_section = ""
    if screenshots_md:
        screenshots_section = f"""## 🎬 视频帧截图

{screenshots_md}
---

"""
    
    # 完整的 Markdown
    md = f"""# {title}

**Tags:** {tags_md}

**Status:** ✅ 已完成

**Author:** {uploader}

**Cover:**
![视频封面]({thumbnail})

---

## 📝 Note

{ai_result.get('note', '*AI 生成失败*')}

---

## 📺 视频信息

**链接:** {webpage_url}
**时长:** {duration}
**UP 主:** {uploader}
**播放:** {view_count:,} | **点赞:** {like_count:,}

---

## 🎯 核心要点

{key_points_md if key_points_md else '*AI 分析中...*'}
---

{concepts_md}{warnings_md}{screenshots_section}## 💡 总结

{ai_result.get('summary', '*AI 生成失败*')}

---

*生成时间：{__import__('datetime').datetime.now().strftime("%Y-%m-%d")}*
*技能版本：video-summarizer v1.5 (AI Enhanced)*
*AI 模型：qwen3.5-plus*
"""
    
    return md


def main():
    if len(sys.argv) < 4:
        print("用法：python3 analyze-subtitles-ai.py <字幕文件> <元数据文件> <输出文件>")
        sys.exit(1)
    
    vtt_file = sys.argv[1]
    meta_file = sys.argv[2]
    output_file = sys.argv[3]
    
    print("=" * 50)
    print("🧠 AI 字幕分析器 v1.5")
    print("=" * 50)
    print()
    
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
        # 降级处理：创建简化版总结
        md_content = f"""# {video_info.get('title', 'Unknown')}

**Tags:** `视频总结` `AI`

**Status:** ⚠️ AI 分析失败

**Author:** {video_info.get('uploader', 'Unknown')}

---

## 📝 Note

AI 分析暂时不可用，请稍后重试。

---

## 📺 视频信息

**链接:** {video_info.get('webpage_url', '')}
**时长:** {video_info.get('duration_string', 'Unknown')}
**UP 主:** {video_info.get('uploader', 'Unknown')}

---

## 🎯 核心要点

*AI 分析失败，无法提取要点*

---

*生成时间：{__import__('datetime').datetime.now().strftime("%Y-%m-%d")}*
*技能版本：video-summarizer v1.5 (AI Enhanced)*
"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"✅ 基础版本已生成：{output_file}")
        return
    
    print()
    
    # 生成 Markdown
    print("📝 生成结构化总结...")
    md_content = generate_markdown(video_info, ai_result)
    
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
