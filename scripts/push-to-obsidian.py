#!/usr/bin/env python3
"""
push-to-obsidian.py - 将视频总结写入 Obsidian Vault
用法：python3 push-to-obsidian.py <output_dir>

功能：
1. 读取 summary.md + metadata.json
2. 生成 YAML frontmatter（Obsidian 兼容）
3. 写入 Vault：3-输出-复盘/视频总结/
4. 拷贝截图/封面到 attachments/ 子目录
5. 转换图片引用为本地相对路径

版本：v1.1.0
"""

import sys
import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
import env_helper  # 统一初始化 AGENT_HOME + 加载 .env

VAULT_PATH = os.getenv('OBSIDIAN_VAULT_PATH', '')
if not VAULT_PATH:
    print("❌ 错误：未配置 OBSIDIAN_VAULT_PATH，跳过 Obsidian 存储")
    print("   在 $AGENT_HOME/.env 中添加：OBSIDIAN_VAULT_PATH=你的Vault路径")
    sys.exit(1)

VAULT = Path(VAULT_PATH)
if not VAULT.exists():
    print(f"❌ 错误：Obsidian Vault 路径不存在：{VAULT}")
    sys.exit(1)

# Vault 内目标目录
TARGET_DIR = VAULT / '1-输入-收件箱' / '视频总结'
ATTACH_DIR = TARGET_DIR / 'attachments'


def load_metadata(output_dir: Path) -> dict:
    """加载 metadata.json"""
    meta_file = output_dir / 'metadata.json'
    if meta_file.exists():
        with open(meta_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def extract_tags_string(summary_path: Path) -> list:
    """从 summary.md 提取 Tags 行"""
    with open(summary_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('**Tags:**'):
                return re.findall(r'`([^`]+)`', line)
    return []


def detect_platform(meta: dict) -> str:
    """从元数据识别平台"""
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

    created = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')

    # 平台中文名
    platform_names = {'bilibili': 'Bilibili', 'youtube': 'YouTube', 'xhs': '小红书', 'douyin': '抖音'}
    platform_cn = platform_names.get(platform, platform)

    lines = ['---']
    lines.append(f'title: "【{platform_cn}】{title}"')
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


def copy_attachments(output_dir: Path) -> list:
    """拷贝截图和封面到 attachments/"""
    ATTACH_DIR.mkdir(parents=True, exist_ok=True)
    copied = []

    # 截图
    screenshots_dir = output_dir / 'screenshots'
    if screenshots_dir.exists():
        for img in sorted(screenshots_dir.iterdir()):
            if img.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.webp'}:
                dest = ATTACH_DIR / img.name
                shutil.copy2(img, dest)
                copied.append(img.name)

    # 封面
    cover_file = output_dir / 'cover.jpg'
    if cover_file.exists():
        dest = ATTACH_DIR / 'cover.jpg'
        shutil.copy2(cover_file, dest)
        if 'cover.jpg' not in copied:
            copied.append('cover.jpg')

    return copied


def convert_image_refs(content: str) -> str:
    """将 HTTP 图片引用转换为本地 attachments/ 相对路径，并移除 OSS URL 引用"""
    # 1. 移除封面图中的 HTTP URL 引用（将被本地 cover.jpg 替代）
    #    ![视频封面](https://...) → ![视频封面](attachments/cover.jpg)
    content = re.sub(
        r'!\[视频封面\]\(https?://[^)]+\)',
        '![视频封面](attachments/cover.jpg)',
        content
    )

    # 2. 保留本地 attachments/ 引用不动
    # 3. 章节截图的 OSS URL 保留（远程可见），但可选添加本地副本引用
    #    对于章节截图，由于它们是外部 OSS URL，不转换为本地路径

    return content


def strip_existing_frontmatter(content: str) -> str:
    """移除 Markdown 中已有的元数据头部（Tags/Author/Cover 行）"""
    lines = content.split('\n')
    result = []
    skip_meta = False

    for line in lines:
        if line.strip() == '---' and not skip_meta:
            skip_meta = True
            continue
        if skip_meta:
            if line.startswith('**Tags:**') or line.startswith('**Author:**') or line.startswith('**Cover:**'):
                continue
            if line.startswith('!['):
                continue  # 跳过旧封面图
            if line.strip() == '---':
                continue
            skip_meta = False
        result.append(line)

    return '\n'.join(result)


def push_to_obsidian(output_dir: str) -> bool:
    """主流程：将视频总结写入 Obsidian Vault"""
    out = Path(output_dir)
    summary_file = out / 'summary.md'

    if not summary_file.exists():
        print(f"❌ summary.md 不存在：{summary_file}")
        return False

    # 加载数据
    meta = load_metadata(out)
    tags = extract_tags_string(summary_file)
    platform = detect_platform(meta)

    # 生成文件名
    video_id = meta.get('id', '') or re.sub(r'[^a-zA-Z0-9_-]', '', meta.get('title', 'video'))[:30]
    date_str = datetime.now().strftime('%Y%m%d')
    filename = f"{platform}_{video_id}_{date_str}.md"

    # 准备目录
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    ATTACH_DIR.mkdir(parents=True, exist_ok=True)

    # 拷贝附件
    copied_files = copy_attachments(out)
    if copied_files:
        print(f"   📎 附件：{', '.join(copied_files)}")

    # 读取并处理内容
    with open(summary_file, 'r', encoding='utf-8') as f:
        raw_content = f.read()

    # 剥离旧元数据头部
    body = strip_existing_frontmatter(raw_content)

    # 转换图片引用
    body = convert_image_refs(body)

    # 生成 frontmatter
    frontmatter = generate_frontmatter(meta, tags, platform)

    # 组合最终内容
    final_content = frontmatter + body

    # 写入 Vault
    target_file = TARGET_DIR / filename
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(final_content)

    # 输出摘要
    print(f"   ✅ Obsidian 存储完成")
    print(f"   📄 {target_file}")
    print(f"   🏷️  标签：{', '.join(tags) if tags else '(无)'}")
    print(f"   📎 附件：{len(copied_files)} 个")

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
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
