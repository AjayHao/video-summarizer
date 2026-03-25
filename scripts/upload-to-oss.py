#!/usr/bin/env python3
"""
阿里云 OSS 图床上传脚本
用于 video-summarizer 技能，自动上传截图到阿里云 OSS

支持：
1. 公开读 Bucket：直接返回永久访问链接
2. 私有 Bucket：返回签名 URL（默认 2 小时有效期）
"""

import os
import sys
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
import time


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
        prefix: OSS 存储路径前缀
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
        # 构建远程键名（包含 screenshots 目录，使用正斜杠）
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


def main():
    parser = argparse.ArgumentParser(description='阿里云 OSS 图床上传工具')
    parser.add_argument('action', choices=['upload', 'batch'], 
                       help='upload: 上传单文件 | batch: 批量上传目录')
    parser.add_argument('path', help='文件路径或目录路径')
    parser.add_argument('--prefix', default='screenshots/', 
                       help='OSS 存储路径前缀（仅 batch 模式）')
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
        # 批量上传
        results = upload_screenshots(args.path, args.prefix, args.public)
        
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
    
    return 0 if all(r.get('success', False) for r in (results if args.action == 'batch' else [result])) else 1


if __name__ == '__main__':
    sys.exit(main())
