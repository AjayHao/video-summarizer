#!/usr/bin/env python3
# analyze-subtitles.py - 分析字幕生成结构化总结
# 用法：python3 analyze-subtitles.py <字幕文件> <视频元数据> <输出文件>

import sys
import json
import re
from datetime import timedelta

def parse_vtt(vtt_file):
    """解析 VTT 字幕文件，返回带时间戳的字幕列表"""
    subtitles = []
    
    with open(vtt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除 WEBVTT 头部
    content = re.sub(r'^WEBVTT.*?\n\n', '', content, flags=re.DOTALL)
    
    # 解析每个字幕块
    pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})\n(.*?)(?=\n\n|\n*$)'
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

def segment_by_topic(subtitles):
    """根据内容将字幕分段（简单版：按时间间隔）"""
    segments = []
    current_segment = []
    
    for i, sub in enumerate(subtitles):
        if not current_segment:
            current_segment.append(sub)
        else:
            # 如果距离上一段超过 30 秒，开始新段落
            prev_end = current_segment[-1]['end']
            curr_start = sub['start']
            
            # 简单判断：如果时间差大，分段
            if len(current_segment) > 10:  # 每段至少 10 句
                segments.append(current_segment)
                current_segment = [sub]
            else:
                current_segment.append(sub)
    
    if current_segment:
        segments.append(current_segment)
    
    return segments

def extract_key_points(subtitles, num_points=5):
    """提取核心要点（简单启发式：找包含关键词的句子）"""
    keywords = ['方法', '第一', '第二', '第三', '第四', '首先', '其次', '最后', 
                '重要的是', '注意', '关键', '总结', '建议']
    
    scored = []
    for i, sub in enumerate(subtitles):
        score = 0
        text = sub['text']
        
        # 包含关键词加分
        for kw in keywords:
            if kw in text:
                score += 2
        
        # 长度适中的句子优先（太短可能不完整，太长可能复杂）
        if 20 < len(text) < 100:
            score += 1
        
        if score > 0:
            scored.append((score, i, sub))
    
    # 按分数排序，取前 N 个
    scored.sort(reverse=True)
    key_points = []
    used_indices = set()
    
    for score, idx, sub in scored:
        if len(key_points) >= num_points:
            break
        # 避免相邻的句子
        if all(abs(idx - ui) > 20 for ui in used_indices):
            key_points.append(sub)
            used_indices.add(idx)
    
    return sorted(key_points, key=lambda x: subtitles.index(x))

def extract_concepts(subtitles):
    """提取关键概念"""
    # 简单提取：找"XX 是"、"叫做 XX"等定义性句子
    concept_patterns = [
        r'(.+?) 就是 (.+?)(?:[，。,.]|$)',
        r'(.+?) 叫做 (.+?)(?:[，。,.]|$)',
        r'(.+?) 是指 (.+?)(?:[，。,.]|$)',
        r'(.+?) 是一种 (.+?)(?:[，。,.]|$)',
    ]
    
    concepts = []
    for sub in subtitles:
        text = sub['text']
        for pattern in concept_patterns:
            match = re.search(pattern, text)
            if match:
                concepts.append({
                    'term': match.group(1).strip(),
                    'definition': match.group(2).strip(),
                    'time': sub['start']
                })
    
    # 去重
    seen = set()
    unique = []
    for c in concepts:
        if c['term'] not in seen:
            seen.add(c['term'])
            unique.append(c)
    
    return unique[:5]  # 最多 5 个概念

def generate_summary(video_meta, subtitles, output_file):
    """生成结构化总结"""
    
    # 提取信息
    title = video_meta.get('title', 'Unknown')
    uploader = video_meta.get('uploader', 'Unknown')
    duration = video_meta.get('duration_string', 'Unknown')
    view_count = video_meta.get('view_count', 0)
    like_count = video_meta.get('like_count', 0)
    thumbnail = video_meta.get('thumbnail', '')
    
    # 分段
    segments = segment_by_topic(subtitles)
    
    # 提取要点
    key_points = extract_key_points(subtitles, num_points=5)
    
    # 提取概念
    concepts = extract_concepts(subtitles)
    
    # 生成 Markdown
    md = f"""# {title}

**Tags:** `视频总结` `AI` `教程`

**Status:** ✅ 已完成

**Author:** {uploader}

**Cover:**
![视频封面]({thumbnail})

---

## 📝 Note

*待 AI 生成概述*

---

## 📺 视频信息

**链接:** {video_meta.get('webpage_url', '')}
**时长:** {duration}
**发布:** {video_meta.get('upload_date', 'Unknown')}
**播放:** {view_count:,} | **点赞:** {like_count:,}

---

## 🎯 核心要点

"""
    
    # 添加核心要点
    for i, point in enumerate(key_points, 1):
        md += f"**要点 {i}** [{point['start']}]\n"
        md += f"{point['text']}\n\n"
    
    md += "---\n\n"
    
    # 添加关键概念
    if concepts:
        md += "## 📚 关键概念\n\n"
        md += "| 概念 | 解释 |\n"
        md += "|------|------|\n"
        for c in concepts:
            md += f"| **{c['term']}** | {c['definition']} `[{c['time']}]` |\n"
        md += "\n---\n\n"
    
    md += """## 💡 总结

*待 AI 生成最终总结*

---

*本总结由 video-summarizer 自动生成*
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"✅ 总结生成完成：{output_file}")

def main():
    if len(sys.argv) < 4:
        print("用法：python3 analyze-subtitles.py <字幕文件> <元数据文件> <输出文件>")
        sys.exit(1)
    
    vtt_file = sys.argv[1]
    meta_file = sys.argv[2]
    output_file = sys.argv[3]
    
    # 解析字幕
    print(f"📝 解析字幕：{vtt_file}")
    subtitles = parse_vtt(vtt_file)
    print(f"   找到 {len(subtitles)} 条字幕")
    
    # 加载元数据
    print(f"📊 加载元数据：{meta_file}")
    with open(meta_file, 'r', encoding='utf-8') as f:
        video_meta = json.load(f)
    
    # 生成总结
    print(f"✍️  生成总结...")
    generate_summary(video_meta, subtitles, output_file)

if __name__ == '__main__':
    main()
