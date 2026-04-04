#!/usr/bin/env python3
"""
阿里云 OSS 图床上传脚本
用于 video-summarizer 技能，自动上传截图到阿里云 OSS

路径规范：
/screenshots/<平台名>/<视频 ID>/<截图文件>

支持平台：
- bilibili (B 站)
- douyin (抖音)
- xhs (小红书)
- youtube (YouTube)
- wxvideo (微信视频)

支持：
1. 公开读 Bucket：直接返回永久访问链接
2. 私有 Bucket：返回签名 URL（默认 2 小时有效期）
"""

import os
import sys
import re
import argparse
from pathlib import Path

# 读取环境变量
from dotenv import load_dotenv
load_dotenv(Path.home() / '.openclaw' / '.env')

# 阿里云 OSS 配置
ALIYUN_OSS_AK = os.getenv('ALIYUN_OSS_AK')
ALIYUN_OSS_SK = os.getenv('ALIYUN_OSS_SK')
ALIYUN_OSS_BUCKET = os.getenv('ALIYUN_OSS_BUCKET_ID')
ALIYUN_OSS_ENDPOINT = os.getenv('ALIYUN_OSS_ENDPOINT')

if not all([ALIYUN_OSS_AK, ALIYUN_OSS_SK, ALIYUN_OSS_BUCKET]):
    print("❌ 错误：缺少阿里云 OSS 配置，请检查 ~/.openclaw/.env", file=sys.stderr)
    sys.exit(1)

import oss2


# 平台识别规则
PLATFORM_PATTERNS = {
    'bilibili': [
        r'bilibili\.com/video/(BV\w+)',
        r'bilibili\.com/video/(av\d+)',
    ],
    'douyin': [
        r'douyin\.com/video/(\d+)',
        r'iesdouyin\.com/share/video/(\d+)',
    ],
    'xhs': [
        r'xiaohongshu\.com/discovery/item/(\w+)',
        r'xhslink\.com/(\w+)',
    ],
    'youtube': [
        r'youtube\.com/watch\?v=([\w-]+)',
        r'youtu\.be/([\w-]+)',
    ],
    'wxvideo': [
        r'channels\.wechat\.com/mp/newfeed/(\d+)',
        r'tencent\.com/video/(\w+)',
    ],
}


def detect_platform(video_url: str) -> tuple:
    """
    从视频 URL 识别平台和视频 ID
    
    Returns:
        tuple: (platform, video_id) 或 (None, None)
    """
    for platform, patterns in PLATFORM_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                video_id = match.group(1)
                # 清理视频 ID，移除特殊字符
                video_id = re.sub(r'[^a-zA-Z0-9_-]', '', video_id)
                return platform, video_id
    
    return None, None


def upload_to_oss(local_file_path: str, remote_key: str = None, public: bool = False, expires: int = 7200) -> dict:
    """
    上传文件到阿里云 OSS
    
    Args:
        local_file_path: 本地文件路径
        remote_key: 远程文件键名（可选，默认使用文件名）
        public: 是否公开访问（True=公开 URL，False=签名 URL）
        expires: 签名 URL 过期时间（秒），默认 2 小时
    
    Returns:
        dict: {
            'success': bool,
            'url': str (成功时),
            'error': str (失败时)
        }
    """
    try:
        # 构建 Auth 和 Bucket 对象
        auth = oss2.Auth(ALIYUN_OSS_AK, ALIYUN_OSS_SK)
        bucket = oss2.Bucket(auth, f'https://{ALIYUN_OSS_ENDPOINT}', ALIYUN_OSS_BUCKET)
        
        # 如果没有指定 remote_key，使用文件名
        if remote_key is None:
            remote_key = Path(local_file_path).name
        
        # 上传文件
        with open(local_file_path, 'rb') as f:
            bucket.put_object(remote_key, f)
        
        # 构建访问 URL
        if public:
            # 公开读 URL
            url = f"https://{ALIYUN_OSS_BUCKET}.{ALIYUN_OSS_ENDPOINT}/{remote_key}"
        else:
            # 签名 URL（私有 Bucket）
            url = bucket.sign_url('GET', remote_key, expires)
        
        return {
            'success': True,
            'url': url,
            'key': remote_key,
            'endpoint': ALIYUN_OSS_ENDPOINT,
            'public': public
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': f"异常：{str(e)}"
        }


def upload_screenshots(screenshots_dir: str, prefix: str = "screenshots/", public: bool = False) -> list:
    """
    批量上传截图目录中的所有图片
    
    Args:
        screenshots_dir: 截图目录路径
        prefix: OSS 存储路径前缀（格式：screenshots/<平台>/<视频 ID>/）
        public: 是否返回公开 URL
    
    Returns:
        list: 上传结果列表，每个元素包含 {local_path, oss_url, success}
    """
    screenshots_path = Path(screenshots_dir)
    if not screenshots_path.exists():
        print(f"❌ 目录不存在：{screenshots_dir}", file=sys.stderr)
        return []
    
    # 获取所有图片文件
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    image_files = sorted([
        f for f in screenshots_path.iterdir() 
        if f.is_file() and f.suffix.lower() in image_extensions
    ])
    
    if not image_files:
        print(f"⚠️ 目录中没有找到图片文件", file=sys.stderr)
        return []
    
    results = []
    for img_file in image_files:
        # 构建远程键名（使用正斜杠）
        remote_key = f"{prefix}{img_file.name}".replace('\\', '/')
        
        print(f"📤 上传：{img_file.name} ...", file=sys.stderr)
        result = upload_to_oss(str(img_file), remote_key, public)
        
        if result['success']:
            print(f"✅ 成功：{result['url'][:60]}...", file=sys.stderr)
            results.append({
                'local_path': str(img_file),
                'oss_url': result['url'],
                'remote_key': result['key'],
                'success': True
            })
        else:
            print(f"❌ 失败：{result['error']}", file=sys.stderr)
            results.append({
                'local_path': str(img_file),
                'error': result['error'],
                'success': False
            })
    
    return results


def build_prefix(video_url: str = None, metadata_file: str = None) -> str:
    """
    构建 OSS 上传路径前缀
    
    格式：/screenshots/<平台名>/<视频 ID>/
    
    Args:
        video_url: 视频 URL（可选）
        metadata_file: 元数据 JSON 文件路径（可选）
    
    Returns:
        str: OSS 路径前缀
    """
    platform = 'unknown'
    video_id = 'unknown'
    
    # 尝试从 URL 识别平台
    if video_url:
        platform, video_id = detect_platform(video_url)
    
    # 如果 URL 识别失败，尝试从元数据文件获取
    if platform == 'unknown' and metadata_file and os.path.exists(metadata_file):
        try:
            import json
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                video_url = metadata.get('webpage_url', '')
                if video_url:
                    platform, video_id = detect_platform(video_url)
                
                # 如果还是未知，使用 uploader 作为备用
                if platform == 'unknown':
                    uploader = metadata.get('uploader', 'unknown')
                    platform = re.sub(r'[^a-zA-Z0-9]', '', uploader)[:20].lower()
                    if not platform:
                        platform = 'unknown'
                
                # 使用视频 ID 或标题
                if video_id == 'unknown':
                    video_id = metadata.get('id', 'unknown')
                    if not video_id or video_id == 'unknown':
                        title = metadata.get('title', 'video')
                        # 从标题生成安全 ID
                        video_id = re.sub(r'[^a-zA-Z0-9]', '', title)[:30].lower()
                        if not video_id:
                            video_id = 'video'
        except Exception as e:
            print(f"⚠️ 读取元数据失败：{e}", file=sys.stderr)
    
    # 构建前缀
    timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
    prefix = f"screenshots/{platform}/{video_id}_{timestamp}/"
    
    print(f"📁 OSS 路径：{prefix}", file=sys.stderr)
    
    return prefix


def main():
    parser = argparse.ArgumentParser(description='阿里云 OSS 图床上传工具')
    parser.add_argument('action', choices=['upload', 'batch', 'auto'], 
                       help='upload: 上传单文件 | batch: 批量上传目录 | auto: 自动识别平台')
    parser.add_argument('path', help='文件路径或目录路径')
    parser.add_argument('--prefix', default=None, 
                       help='OSS 存储路径前缀（auto 模式自动识别）')
    parser.add_argument('--video-url', default=None,
                       help='视频 URL（auto 模式用于识别平台）')
    parser.add_argument('--metadata', default=None,
                       help='元数据 JSON 文件路径（auto 模式备用）')
    parser.add_argument('--public', action='store_true',
                       help='返回公开 URL（需要 Bucket 配置为公开读）')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='输出格式')
    
    args = parser.parse_args()
    
    if args.action == 'upload':
        # 单文件上传
        result = upload_to_oss(args.path, public=args.public)
        if args.format == 'json':
            import json
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if result['success']:
                print(f"✅ 上传成功")
                print(f"📎 URL: {result['url']}")
                print(f"🔑 Key: {result['key']}")
                print(f"🌍 Endpoint: {result['endpoint']}")
            else:
                print(f"❌ 上传失败：{result['error']}")
                sys.exit(1)
    
    elif args.action == 'batch':
        # 批量上传（使用指定前缀）
        prefix = args.prefix or f"screenshots/unknown/unknown_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}/"
        results = upload_screenshots(args.path, prefix, args.public)
        
        if args.format == 'json':
            import json
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            success_count = sum(1 for r in results if r['success'])
            total_count = len(results)
            print(f"\n📊 上传完成：{success_count}/{total_count} 成功")
            
            if success_count > 0:
                print("\n📎 访问链接:")
                for r in results:
                    if r['success']:
                        print(f"  - {r['oss_url'][:70]}...")
    
    elif args.action == 'auto':
        # 自动识别平台并上传
        print("🔍 自动识别平台...", file=sys.stderr)
        prefix = build_prefix(args.video_url, args.metadata)
        
        results = upload_screenshots(args.path, prefix, args.public)
        
        if args.format == 'json':
            import json
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            success_count = sum(1 for r in results if r['success'])
            total_count = len(results)
            print(f"\n📊 上传完成：{success_count}/{total_count} 成功")
            
            if success_count > 0:
                print("\n📎 访问链接:")
                for r in results:
                    if r['success']:
                        print(f"  - {r['oss_url'][:70]}...")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
