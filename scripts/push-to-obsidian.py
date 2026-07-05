#!/usr/bin/env python3
"""
push-to-obsidian.py - 将视频总结写入 Obsidian Vault
用法：python3 push-to-obsidian.py <output_dir>

功能：
1. 读取 summary.md + metadata.json
2. 生成 YAML frontmatter（Obsidian 兼容）
3. 写入 Vault：1-输入-收件箱/视频总结/
4. 图片引用保留 OSS URL，不拷贝本地附件

版本：v1.1.0
"""

import sys
import os
import re
import json
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
import config  # 统一初始化 AGENT_HOME + 加载 .env

VAULT_PATH = os.getenv('OBSIDIAN_VAULT_PATH', '')
if not VAULT_PATH:
    print("❌ 错误：未配置 OBSIDIAN_VAULT_PATH，跳过 Obsidian 存储")
    print("   在 $AGENT_HOME/.env 中添加：OBSIDIAN_VAULT_PATH=你的Vault路径")
    sys.exit(1)

VAULT = Path(VAULT_PATH)
if not VAULT.exists():
    print(f"❌ 错误：Obsidian Vault 路径不存在：{VAULT}")
    sys.exit(1)

TARGET_DIR = VAULT / '1-收件箱' / '视频总结'


def load_metadata(output_dir: Path) -> dict:
    meta_file = output_dir / 'metadata.json'
    if meta_file.exists():
        with open(meta_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_oss_urls(output_dir: Path) -> list:
    """加载 OSS 截图 URL 列表"""
    urls_file = output_dir / 'screenshot_urls.txt'
    if urls_file.exists():
        with open(urls_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [x.get('oss_url', '') for x in data if x.get('success') and x.get('oss_url')]
    return []


def load_cover_url(output_dir: Path) -> str:
    """加载 OSS 封面 URL"""
    cover_file = output_dir / 'cover_url.txt'
    if cover_file.exists():
        data = json.loads(cover_file.read_text(encoding='utf-8'))
        return data.get('oss_url', '')
    return ''


def extract_tags_string(summary_path: Path) -> list:
    with open(summary_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('**Tags:**'):
                return re.findall(r'`([^`]+)`', line)
    return []


def detect_platform(meta: dict) -> str:
    platform = meta.get('platform', '')
    if platform:
        return platform
    url = meta.get('webpage_url', '')
    if 'bilibili.com' in url or 'b23.tv' in url:
        return 'bilibili'
    if 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    if 'xiaohongshu.com' in url or 'xhslink.com' in url:
        return 'xhs'
    if 'douyin.com' in url or 'iesdouyin.com' in url or 'v.douyin.com' in url:
        return 'douyin'
    return 'unknown'


def safe_filename(title: str) -> str:
    """生成安全的文件名（保留中文）"""
    # 移除文件系统不允许的字符
    safe = re.sub(r'[\\/:*?"<>|]', '', title)
    # 截断过长文件名
    return safe[:60]


def generate_frontmatter(meta: dict, tags: list, platform: str) -> str:
    """生成 Obsidian YAML frontmatter"""
    title = meta.get('title', 'Untitled')
    author = meta.get('uploader', '')
    duration = meta.get('duration_string', '')
    source_url = meta.get('webpage_url', '')

    # 格式化日期
    upload_date = meta.get('upload_date', '')
    if upload_date and isinstance(upload_date, str) and len(upload_date) == 8:
        date_str = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')

    created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    lines = ['---']
    lines.append(f'title: "{title}"')
    if tags:
        lines.append(f'tags: [{", ".join(tags)}]')
    lines.append(f'platform: {platform}')
    if author:
        lines.append(f'author: "{author}"')
    if duration:
        lines.append(f'duration: "{duration}"')
    if source_url:
        lines.append(f'source_url: {source_url}')
    lines.append(f'date: {date_str}')
    lines.append(f'created: {created}')
    lines.append('status: inbox')
    lines.append('---')
    lines.append('')
    return '\n'.join(lines)


def fix_image_refs(content: str, oss_urls: list, cover_url: str) -> str:
    """修正图片引用：封面用 OSS URL，章节截图逐个替换 OSS URL，多余的移除"""
    # 1. 封面图 → OSS 封面 URL
    if cover_url:
        content = re.sub(
            r'!\[视频封面\]\([^)]+\)',
            f'![视频封面]({cover_url})',
            content
        )
    # 2. 章节截图：逐个替换为 OSS URL，多余的删掉（不保留重复封面）
    if oss_urls:
        remaining = list(oss_urls)
        def replace_chapter(match):
            if remaining:
                return f'![章节截图]({remaining.pop(0)})'
            return ''  # URL 用完，删除多余引用
        content = re.sub(r'!\[章节截图\]\([^)]+\)\n?', replace_chapter, content)
    else:
        # 无 OSS URL，全部移除
        content = re.sub(r'!\[章节截图\]\([^)]+\)\n?', '', content)
    return content


def strip_metadata_header(content: str) -> str:
    """移除 Markdown 中的元数据头部（Tags/Author/Cover 行）"""
    lines = content.split('\n')
    result = []
    skip = False
    for line in lines:
        if line.strip() == '---' and not skip:
            skip = True
            continue
        if skip:
            if line.startswith('**Tags:**') or line.startswith('**Author:**') or line.startswith('**Cover:**'):
                continue
            if line.startswith('!['):
                continue
            if line.strip() == '---':
                continue
            skip = False
        result.append(line)
    return '\n'.join(result)


def push_to_obsidian(output_dir: str) -> bool:
    out = Path(output_dir)
    summary_file = out / 'summary.md'

    if not summary_file.exists():
        print(f"❌ summary.md 不存在：{summary_file}")
        return False

    meta = load_metadata(out)
    tags = extract_tags_string(summary_file)
    oss_urls = load_oss_urls(out)
    cover_url = load_cover_url(out)
    platform = detect_platform(meta)

    # 文件名：用视频标题
    title = meta.get('title', 'video')
    filename = f"{safe_filename(title)}.md"

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    # 读取内容
    raw_content = summary_file.read_text(encoding='utf-8')

    # 处理
    body = strip_metadata_header(raw_content)
    body = fix_image_refs(body, oss_urls, cover_url)
    frontmatter = generate_frontmatter(meta, tags, platform)

    # 写入
    target_file = TARGET_DIR / filename
    target_file.write_text(frontmatter + body, encoding='utf-8')

    print(f"   ✅ Obsidian 存储完成")
    print(f"   📄 {target_file}")
    print(f"   🏷️  标签：{', '.join(tags) if tags else '(无)'}")
    print(f"   🖼️  截图引用：{len(oss_urls)} 张（OSS URL）")

    return True


def main():
    if len(sys.argv) < 2:
        print("用法：python3 push-to-obsidian.py <output_dir>")
        sys.exit(1)

    output_dir = sys.argv[1]
    print("📓 Obsidian 本地存储")
    print(f"   Vault：{VAULT}")

    success = push_to_obsidian(output_dir)
    if success:
        print()
        print("=" * 50)
        print("✨ Obsidian 写入完成！")
        print("=" * 50)
        return 0
    return 1


if __name__ == '__main__':
    sys.exit(main())
