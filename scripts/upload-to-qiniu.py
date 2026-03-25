#!/usr/bin/env python3
"""
七牛云图床上传脚本
用于 video-summarizer 技能，自动上传截图到七牛云对象存储

使用七牛云标准 API（非 S3 兼容），支持公开/私有空间
"""

import os
import sys
import argparse
from pathlib import Path

# 读取环境变量
from dotenv import load_dotenv
load_dotenv(Path.home() / '.openclaw' / '.env')

# 七牛云配置
QINIU_AK = os.getenv('QINIU_AK')
QINIU_SK = os.getenv('QINIU_SK')
QINIU_BUCKET = os.getenv('QINIU_BUCKET_ID')
QINIU_DOMAIN = os.getenv('QINIU_DOMAIN')  # 公开访问域名（必填）

if not all([QINIU_AK, QINIU_SK, QINIU_BUCKET]):
    print("❌ 错误：缺少七牛云配置，请检查 ~/.openclaw/.env", file=sys.stderr)
    sys.exit(1)

from qiniu import Auth, put_file
import qiniu.config


def upload_to_qiniu(local_file_path: str, remote_key: str = None) -> dict:
    """
    上传文件到七牛云
    
    Args:
        local_file_path: 本地文件路径
        remote_key: 远程文件键名（可选，默认使用文件名）
    
    Returns:
        dict: {
            'success': bool,
            'url': str (成功时),
            'error': str (失败时)
        }
    """
    try:
        # 构建 Auth 对象
        q = Auth(QINIU_AK, QINIU_SK)
        
        # 生成上传凭证
        token = q.upload_token(QINIU_BUCKET)
        
        # 如果没有指定 remote_key，使用文件名
        if remote_key is None:
            remote_key = Path(local_file_path).name
        
        # 上传文件
        ret, info = put_file(token, remote_key, local_file_path)
        
        if info.status_code == 200:
            # 构建访问 URL
            if QINIU_DOMAIN:
                # 使用配置的域名（公开空间）
                url = f"{QINIU_DOMAIN}/{remote_key}"
            else:
                # 未配置域名，返回提示
                url = None
            
            return {
                'success': True,
                'url': url,
                'key': remote_key,
                'hash': ret.get('hash', ''),
                'message': '上传成功，请配置 QINIU_DOMAIN 以获取访问链接' if not url else None
            }
        else:
            return {
                'success': False,
                'error': f"上传失败：{info.status_code} - {info.error}"
            }
    
    except Exception as e:
        return {
            'success': False,
            'error': f"异常：{str(e)}"
        }


def upload_screenshots(screenshots_dir: str, prefix: str = "screenshots/") -> list:
    """
    批量上传截图目录中的所有图片
    
    Args:
        screenshots_dir: 截图目录路径
        prefix: 七牛云存储路径前缀
    
    Returns:
        list: 上传结果列表，每个元素包含 {local_path, qiniu_url, success}
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
        # 构建远程键名（包含 screenshots 目录）
        remote_key = f"{prefix}{img_file.name}"
        
        print(f"📤 上传：{img_file.name} ...", file=sys.stderr)
        result = upload_to_qiniu(str(img_file), remote_key)
        
        if result['success']:
            print(f"✅ 成功：{result['url'] or result['message']}", file=sys.stderr)
            results.append({
                'local_path': str(img_file),
                'qiniu_url': result['url'],
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
    parser = argparse.ArgumentParser(description='七牛云图床上传工具')
    parser.add_argument('action', choices=['upload', 'batch'], 
                       help='upload: 上传单文件 | batch: 批量上传目录')
    parser.add_argument('path', help='文件路径或目录路径')
    parser.add_argument('--prefix', default='screenshots/', 
                       help='七牛云存储路径前缀（仅 batch 模式）')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='输出格式')
    
    args = parser.parse_args()
    
    if args.action == 'upload':
        # 单文件上传
        result = upload_to_qiniu(args.path)
        if args.format == 'json':
            import json
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if result['success']:
                print(f"✅ 上传成功")
                if result['url']:
                    print(f"📎 URL: {result['url']}")
                if result['message']:
                    print(f"💡 {result['message']}")
                print(f"🔑 Key: {result['key']}")
            else:
                print(f"❌ 上传失败：{result['error']}")
                sys.exit(1)
    
    elif args.action == 'batch':
        # 批量上传
        results = upload_screenshots(args.path, args.prefix)
        
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
                    if r['success'] and r['qiniu_url']:
                        print(f"  - {r['qiniu_url']}")
                    elif r['success']:
                        print(f"  - (待配置 QINIU_DOMAIN)")
    
    return 0 if all(r.get('success', False) for r in (results if args.action == 'batch' else [result])) else 1


if __name__ == '__main__':
    sys.exit(main())
