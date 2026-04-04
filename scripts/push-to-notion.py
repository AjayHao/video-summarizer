#!/usr/bin/env python3
"""
push-to-notion.py - 将视频总结推送到 Notion
用法：python3 push-to-notion.py <summary.md> [Notion Database ID]
"""

import sys
import os
import re
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# 读取环境变量
load_dotenv(Path.home() / '.openclaw' / '.env')

NOTION_API_KEY = os.getenv('NOTION_API_KEY')
NOTION_DATABASE_ID = os.getenv('NOTION_VIDEO_SUMMARY_DATABASE_ID')

if not NOTION_API_KEY:
    print("❌ 错误：缺少 NOTION_API_KEY，请检查 ~/.openclaw/.env")
    sys.exit(1)

# Notion API 配置
NOTION_VERSION = "2025-09-03"
HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}


def parse_markdown(md_file):
    """解析 Markdown 文件，提取关键信息"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取标题
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "视频总结"
    
    # 提取 Note
    note_match = re.search(r'## 📝 Note\n\n(.*?)(?=\n---|\n##)', content, re.DOTALL)
    note = note_match.group(1).strip() if note_match else ""
    
    # 提取 Tags
    tags_match = re.search(r'\*\*Tags:\*\*\s*(.+)$', content, re.MULTILINE)
    tags = []
    if tags_match:
        tags = re.findall(r'`([^`]+)`', tags_match.group(1))
    
    # 提取 UP 主
    author_match = re.search(r'\*\*Author:\*\*\s*(.+)$', content, re.MULTILINE)
    author = author_match.group(1).strip() if author_match else ""
    
    # 提取视频链接
    link_match = re.search(r'\*\*链接:\*\*\s*(.+)$', content, re.MULTILINE)
    video_url = link_match.group(1).strip() if link_match else ""
    
    # 提取时长
    duration_match = re.search(r'\*\*时长:\*\*\s*(.+)$', content, re.MULTILINE)
    duration = duration_match.group(1).strip() if duration_match else ""
    
    # 提取发布日期
    publish_match = re.search(r'\*\*发布:\*\*\s*(.+)$', content, re.MULTILINE)
    publish_date = publish_match.group(1).strip() if publish_match else ""
    
    # 提取封面图片 URL（优先从 Markdown 中提取）
    cover_match = re.search(r'!\[视频封面\]\(([^)]+)\)', content)
    cover_url = cover_match.group(1).strip() if cover_match else ""
    
    # 如果 Markdown 中没有封面，尝试从同级目录的 metadata.json 获取
    if not cover_url:
        md_dir = Path(md_file).parent
        metadata_file = md_dir / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                cover_url = metadata.get('thumbnail', '')
            except:
                pass
    
    # 如果还没有封面，尝试使用第一张截图作为封面
    if not cover_url:
        # 查找 OSS 截图链接（在 Markdown 中）
        # 格式可能是 ![00:00:00](URL) 或 ![章节截图](URL)
        screenshot_matches = re.findall(r'!\[[^\]]+\]\((https?://[^)]+)\)', content)
        if screenshot_matches:
            # 取第一张截图作为封面
            cover_url = screenshot_matches[0].strip()
    
    # 从视频 URL 提取平台来源
    source = "Unknown"
    if video_url:
        if "bilibili.com" in video_url or "b23.tv" in video_url:
            source = "Bilibili"
        elif "xiaohongshu.com" in video_url:
            source = "小红书"
        elif "douyin.com" in video_url:
            source = "抖音"
        elif "youtube.com" in video_url or "youtu.be" in video_url:
            source = "YouTube"
        elif "channels.weixin.qq.com" in video_url:
            source = "微信视频"
    
    return {
        'title': title,
        'note': note,
        'tags': tags,
        'author': author,
        'video_url': video_url,
        'duration': duration,
        'publish_date': publish_date,
        'cover_url': cover_url,
        'source': source,
        'full_content': content
    }


def search_database(database_id):
    """查询 Notion Database（Data Source）"""
    url = f"https://api.notion.com/v1/data_sources/{database_id}/query"
    response = requests.post(url, headers=HEADERS, json={})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ 查询 Database 失败：{response.status_code}")
        print(response.text[:200])
        return None


def create_page_in_database(database_id, properties, blocks=None):
    """在 Notion Database 中创建页面"""
    url = "https://api.notion.com/v1/pages"
    
    data = {
        "parent": {"database_id": database_id},
        "properties": properties
    }
    
    if blocks:
        # 如果需要添加内容块
        pass
    
    # 超时重试机制
    for attempt in range(3):
        try:
            timeout = 30 * (attempt + 1)  # 30s, 60s, 90s
            response = requests.post(url, headers=HEADERS, json=data, timeout=timeout)
            if response.status_code == 200:
                break
            elif response.status_code == 400:
                # 验证错误，直接返回让上层处理
                break
        except requests.exceptions.Timeout:
            print(f"   ⚠️  网络超时，尝试 {attempt + 2}/3...")
            if attempt == 2:
                raise
    
    if response.status_code == 200:
        page_data = response.json()
        page_id = page_data['id']
        page_url = page_data.get('url', '')
        return page_id, page_url
    else:
        print(f"❌ 创建页面失败：{response.status_code}")
        print(f"错误信息：{response.text[:300]}")
        return None, None


def append_blocks_to_page(page_id, blocks):
    """向页面添加内容块"""
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    
    # 超时重试机制
    for attempt in range(3):
        try:
            timeout = 30 * (attempt + 1)  # 30s, 60s, 90s
            response = requests.patch(url, headers=HEADERS, json={"children": blocks}, timeout=timeout)
            if response.status_code == 200:
                return True
            elif response.status_code == 400:
                print(f"❌ 添加内容块失败：{response.status_code}")
                print(response.text[:300])
                return False
        except requests.exceptions.Timeout:
            print(f"   ⚠️  网络超时，尝试 {attempt + 2}/3...")
            if attempt == 2:
                raise
    
    return False


def parse_inline_markdown(text):
    """
    解析行内 Markdown 格式（粗体、斜体、代码、链接）
    返回 Notion rich_text 数组
    """
    rich_text = []
    remaining = text
    
    while remaining:
        # 粗体 **text**
        bold_match = re.match(r'^(.*?)\*\*([^*]+)\*\*(.*)$', remaining)
        if bold_match:
            before, bold_content, after = bold_match.groups()
            if before:
                rich_text.append({"type": "text", "text": {"content": before}})
            rich_text.append({"type": "text", "text": {"content": bold_content, }})
            remaining = after
            continue
        
        # 斜体 *text*（单独一个星号）
        italic_match = re.match(r'^(.*?)(?<!\*)\*([^*]+)\*(?!\*)(.*)$', remaining)
        if italic_match:
            before, italic_content, after = italic_match.groups()
            if before:
                rich_text.append({"type": "text", "text": {"content": before}})
            rich_text.append({"type": "text", "text": {"content": italic_content, }})
            remaining = after
            continue
        
        # 行内代码 `code`
        code_match = re.match(r'^(.*?)`([^`]+)`(.*)$', remaining)
        if code_match:
            before, code_content, after = code_match.groups()
            if before:
                rich_text.append({"type": "text", "text": {"content": before}})
            rich_text.append({"type": "text", "text": {"content": code_content, }})
            remaining = after
            continue
        
        # 链接 [text](url)
        link_match = re.match(r'^(.*?)\[([^\]]+)\]\(([^)]+)\)(.*)$', remaining)
        if link_match:
            before, link_text, link_url, after = link_match.groups()
            if before:
                rich_text.append({"type": "text", "text": {"content": before}})
            rich_text.append({"type": "text", "text": {"content": link_text, "link": {"url": link_url}}})
            remaining = after
            continue
        
        # 时间戳 `[MM:SS]` 保持原样
        time_match = re.match(r'^(.*?)`\[([^`\]]+)\]`(.*)$', remaining)
        if time_match:
            before, time_content, after = time_match.groups()
            if before:
                rich_text.append({"type": "text", "text": {"content": before}})
            rich_text.append({"type": "text", "text": {"content": f"[{time_content}]", }})
            remaining = after
            continue
        
        # 没有更多格式，添加剩余文本
        rich_text.append({"type": "text", "text": {"content": remaining}})
        break
    
    return rich_text


def markdown_to_notion_blocks(markdown_content):
    """将 Markdown 转换为 Notion Blocks"""
    blocks = []
    lines = markdown_content.split('\n')
    
    current_list = []
    in_code_block = False
    code_content = []
    code_language = ""
    in_table = False
    table_rows = []
    
    def flush_table():
        """提交表格"""
        nonlocal in_table, table_rows
        if not in_table or len(table_rows) < 2:
            table_rows = []
            in_table = False
            return
        
        # 第一行是表头
        header_row = table_rows[0]
        # 第二行是分隔符（|---|---|），跳过
        # 从第三行开始是数据行
        data_rows = table_rows[2:] if len(table_rows) > 2 else []
        
        # 创建表格块
        blocks.append({
            "object": "block",
            "type": "table",
            "table": {
                "table_width": len(header_row),
                "has_column_header": True,
                "children": [
                    {
                        "type": "table_row",
                        "table_row": {
                            "cells": [parse_inline_markdown(cell) for cell in header_row]
                        }
                    }
                ] + [
                    {
                        "type": "table_row",
                        "table_row": {
                            "cells": [parse_inline_markdown(cell) for cell in row]
                        }
                    }
                    for row in data_rows
                ]
            }
        })
        table_rows = []
        in_table = False
    
    def flush_list():
        """提交当前列表"""
        nonlocal current_list
        if not current_list:
            return
        for item in current_list:
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": parse_inline_markdown(item)
                }
            })
        current_list = []
    
    for line in lines:
        # 图片处理（优先）- 格式：![alt](url)
        img_match = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)$', line.strip())
        if img_match:
            alt_text = img_match.group(1)
            img_url = img_match.group(2)
            blocks.append({
                "object": "block",
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {"url": img_url}
                }
            })
            continue
        
        # 代码块处理
        if line.startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_language = line[3:].strip()
                code_content = []
            else:
                if code_content:
                    blocks.append({
                        "object": "block",
                        "type": "code",
                        "code": {
                            "rich_text": [{"type": "text", "text": {"content": '\n'.join(code_content)}}],
                            "language": code_language if code_language else "plain text"
                        }
                    })
                in_code_block = False
            continue
        
        if in_code_block:
            code_content.append(line)
            continue
        
        # 表格处理
        stripped = line.strip()
        if stripped.startswith('|') and stripped.endswith('|'):
            if not in_table:
                in_table = True
                table_rows = []
            
            # 解析表格行
            cells = [cell.strip() for cell in stripped.split('|')[1:-1]]
            # 跳过分隔符行（|---|---|）
            if not (len(cells) > 0 and all(c.replace('-', '').replace(':', '') == '' for c in cells)):
                table_rows.append(cells)
            continue
        elif in_table:
            flush_table()
        
        # 标题处理
        if line.startswith('# '):
            flush_table()
            flush_list()  # 刷新列表
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": parse_inline_markdown(line[2:].strip())
                }
            })
        elif line.startswith('## '):
            flush_table()
            flush_list()  # 刷新列表
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": parse_inline_markdown(line[3:].strip())
                }
            })
        elif line.startswith('### '):
            flush_table()
            flush_list()  # 刷新列表
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": parse_inline_markdown(line[4:].strip())
                }
            })
        # 列表处理
        elif line.startswith('- ') or line.startswith('* '):
            current_list.append(line[2:].strip())
        # 空行
        elif not line.strip():
            flush_table()
            flush_list()
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": ""}}]
                }
            })
        # 普通段落
        else:
            flush_table()
            flush_list()
            
            # 普通段落，解析行内格式
            text = line.strip()
            if text:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": parse_inline_markdown(text)
                    }
                })
    
    # 处理剩余的列表
    flush_list()
    
    # 处理剩余的表格
    if in_table:
        flush_table()
    
    return blocks


def push_to_notion(md_file, database_id=None):
    """推送视频总结到 Notion"""
    
    # 使用配置的 Database ID 或参数
    db_id = database_id or NOTION_DATABASE_ID
    
    if not db_id:
        print("❌ 错误：未指定 Notion Database ID")
        print("用法：python3 push-to-notion.py <summary.md> [database_id]")
        print("或在 ~/.openclaw/.env 中配置 NOTION_VIDEO_SUMMARY_DATABASE_ID")
        return None, None
    
    # 解析 Markdown
    print(f"📝 解析 Markdown 文件：{md_file}")
    data = parse_markdown(md_file)
    
    print(f"   标题：{data['title']}")
    print(f"   UP 主：{data['author']}")
    print(f"   标签：{', '.join(data['tags'])}")
    print(f"   来源：{data.get('source', 'Unknown')}")
    print(f"   封面：{data.get('cover_url', 'N/A')}")
    
    # 构建页面属性（适配 Notion 数据库字段类型）
    # 字段类型：Name=title, Source=rich_text, Author=rich_text, Url=url, 
    #           Tags=multi_select, PubDate=date, Length=rich_text, Cover=files
    properties = {
        "Name": {
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": data['title'][:200]  # 限制标题长度
                    }
                }
            ]
        },
        "Source": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": data.get('source', 'Unknown')
                    }
                }
            ]
        },
        "Author": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": data['author']
                    }
                }
            ]
        },
        "Url": {
            "url": data['video_url']
        },
        "Tags": {
            "multi_select": [
                {"name": tag} for tag in data['tags'][:5]  # 最多 5 个标签
            ]
        },
        "PubDate": {
            "date": {
                "start": data['publish_date']
            }
        },
        "Length": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": data['duration']
                    }
                }
            ]
        }
    }
    
    # 仅在封面 URL 有效时添加 Cover 字段
    if data.get('cover_url'):
        properties["Cover"] = {
            "files": [
                {
                    "name": "封面图片",
                    "type": "external",
                    "external": {
                        "url": data['cover_url']
                    }
                }
            ]
        }
    
    # 创建页面（容错：如果字段不存在则移除后重试）
    print(f"📤 创建 Notion 页面...")
    page_id, page_url = create_page_in_database(db_id, properties)
    
    # 如果失败，分析错误原因并尝试修复
    if not page_id:
        print("⚠️  创建失败，尝试移除可选字段后重试...")
        # 只移除 Cover 字段（封面是可选的，其他字段必须保留）
        if "Cover" in properties:
            del properties["Cover"]
            print(f"   移除字段：Cover")
            page_id, page_url = create_page_in_database(db_id, properties)
    
    if not page_id:
        return None, None
    
    print(f"✅ 页面创建成功：{page_url}")
    
    # 添加内容块（Note + 完整内容）
    print(f"📝 添加页面内容...")
    
    # 构建内容块
    blocks = []
    
    # 添加 Note
    if data['note']:
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "📝 概述"}}]
            }
        })
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": data['note']}}]
            }
        })
    
    # 读取完整 Markdown 文件，转换为 blocks（分批发送）
    print(f"📝 转换 Markdown 为 Notion 块...")
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 跳过元数据头部（前 3 个分隔线之间的内容）
    md_lines = md_content.split('\n')
    content_lines = []
    separator_count = 0
    in_metadata = True
    
    for line in md_lines:
        if line.strip() == '---':
            separator_count += 1
            if separator_count >= 3:
                in_metadata = False
            continue
        if in_metadata:
            continue
        # 跳过元数据行
        if line.startswith('**Tags:**') or line.startswith('**Status:**') or line.startswith('**Author:**') or line.startswith('**Cover:**'):
            continue
        if line.strip():  # 跳过空行
            content_lines.append(line)
    
    md_content_clean = '\n'.join(content_lines)
    content_blocks = markdown_to_notion_blocks(md_content_clean)
    
    # 分批发送（Notion 限制每次最多 100 个块）
    batch_size = 100
    total_batches = (len(content_blocks) + batch_size - 1) // batch_size
    print(f"   共 {len(content_blocks)} 个块，分 {total_batches} 批发送...")
    
    for i in range(0, len(content_blocks), batch_size):
        batch = content_blocks[i:i + batch_size]
        batch_num = i // batch_size + 1
        print(f"   发送批次 {batch_num}/{total_batches}...")
        success = append_blocks_to_page(page_id, batch)
        if success:
            print(f"   ✅ 批次 {batch_num} 成功")
        else:
            print(f"   ⚠️ 批次 {batch_num} 失败，继续下一批")
    
    print(f"✅ 内容添加完成")
    return page_id, page_url


def main():
    if len(sys.argv) < 2:
        print("用法：python3 push-to-notion.py <summary.md> [Notion Database ID]")
        sys.exit(1)
    
    md_file = sys.argv[1]
    database_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(md_file):
        print(f"❌ 文件不存在：{md_file}")
        sys.exit(1)
    
    print("=" * 50)
    print("📤 Notion 推送工具")
    print("=" * 50)
    print()
    
    page_id, page_url = push_to_notion(md_file, database_id)
    
    print()
    print("=" * 50)
    if page_url:
        print(f"✅ 推送完成！")
        print(f"📎 Notion 链接：{page_url}")
    else:
        print(f"❌ 推送失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
