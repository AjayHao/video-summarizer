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
    
    return {
        'title': title,
        'note': note,
        'tags': tags,
        'author': author,
        'video_url': video_url,
        'duration': duration,
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
    
    response = requests.post(url, headers=HEADERS, json=data)
    
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
    
    response = requests.patch(url, headers=HEADERS, json={"children": blocks})
    
    if response.status_code == 200:
        return True
    else:
        print(f"❌ 添加内容块失败：{response.status_code}")
        print(response.text[:300])
        return False


def markdown_to_notion_blocks(markdown_content):
    """将 Markdown 转换为 Notion Blocks"""
    blocks = []
    lines = markdown_content.split('\n')
    
    current_list = []
    in_code_block = False
    code_content = []
    code_language = ""
    
    for line in lines:
        # 代码块处理
        if line.startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_language = line[3:].strip()
                code_content = []
            else:
                # 结束代码块
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
        
        # 标题处理
        if line.startswith('# '):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": line[2:].strip()}}]
                }
            })
        elif line.startswith('## '):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": line[3:].strip()}}]
                }
            })
        elif line.startswith('### '):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": line[4:].strip()}}]
                }
            })
        # 列表处理
        elif line.startswith('- ') or line.startswith('* '):
            current_list.append(line[2:].strip())
        # 表格处理（简化版，作为段落）
        elif line.startswith('|'):
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": line}}]
                }
            })
        # 空行
        elif not line.strip():
            if current_list:
                # 提交列表
                for item in current_list:
                    blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": item}}]
                        }
                    })
                current_list = []
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": ""}}]
                }
            })
        # 普通段落
        else:
            if current_list:
                for item in current_list:
                    blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": item}}]
                        }
                    })
                current_list = []
            
            # 检查是否是粗体开头的段落
            text = line.strip()
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": text}}]
                }
            })
    
    # 处理剩余的列表
    if current_list:
        for item in current_list:
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": item}}]
                }
            })
    
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
    
    # 构建页面属性
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
        "UP 主": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": data['author']
                    }
                }
            ]
        },
        "视频链接": {
            "url": data['video_url']
        },
        "时长": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": data['duration']
                    }
                }
            ]
        },
        "标签": {
            "multi_select": [
                {"name": tag} for tag in data['tags'][:5]  # 最多 5 个标签
            ]
        },
        "状态": {
            "select": {
                "name": "✅ 已完成"
            }
        }
    }
    
    # 创建页面
    print(f"📤 创建 Notion 页面...")
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
    
    # 添加分隔线
    blocks.append({
        "object": "block",
        "type": "divider",
        "divider": {}
    })
    
    # 转换完整 Markdown 为 Blocks
    content_blocks = markdown_to_notion_blocks(data['full_content'])
    blocks.extend(content_blocks[:100])  # Notion 限制每次最多 100 个块
    
    # 追加到页面
    if blocks:
        success = append_blocks_to_page(page_id, blocks)
        if success:
            print(f"✅ 内容添加成功")
    
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
