#!/usr/bin/env python3
"""
transcribe-audio.py - Plan B: 语音转录字幕
支持：本地 Whisper 或 Groq API

用法：python3 transcribe-audio.py <音频文件> [输出字幕文件]
"""

import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / '.openclaw' / '.env')

# 配置
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
SILICONFLOW_API_KEY = os.getenv('SILICONFLOW_API_KEY') or os.getenv('API_KEY')
WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'whisper-large-v3')
USE_LOCAL_WHISPER = os.getenv('USE_LOCAL_WHISPER', 'false').lower() == 'true'


def transcribe_with_groq(audio_file: str) -> dict:
    """使用 Groq API 转录音频"""
    import requests
    
    print("   🌐 使用 Groq API 转录...")
    
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    
    with open(audio_file, 'rb') as f:
        files = {"file": f}
        data = {
            "model": "whisper-large-v3",
            "response_format": "verbose_json"
        }
        
        response = requests.post(url, headers=headers, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        return {
            'success': True,
            'text': result.get('text', ''),
            'segments': result.get('segments', [])
        }
    else:
        return {
            'success': False,
            'error': f"Groq API 错误：{response.status_code} - {response.text[:200]}"
        }


def transcribe_with_siliconflow(audio_file: str) -> dict:
    """使用硅基流动 API 转录音频（参考 agent-reach 实现）"""
    import requests
    import time
    
    print("   🌐 使用硅基流动 API 转录 (SenseVoice)...")
    
    try:
        # 硅基流动 API 端点
        api_url = "https://api.siliconflow.cn/v1/audio/transcriptions"
        headers = {
            "Authorization": f"Bearer {SILICONFLOW_API_KEY}"
        }
        
        # 上传音频文件
        with open(audio_file, 'rb') as f:
            files = {'file': f}
            data = {
                'model': 'FunAudioLLM/SenseVoiceSmall',
                'response_format': 'verbose_json',
                'language': 'zh'
            }
            
            response = requests.post(api_url, headers=headers, files=files, data=data, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'text': result.get('text', ''),
                'segments': result.get('segments', [])
            }
        else:
            return {
                'success': False,
                'error': f"硅基流动 API 错误：{response.status_code} - {response.text[:200]}"
            }
    except Exception as e:
        return {
            'success': False,
            'error': f"硅基流动 API 异常：{str(e)}"
        }


def transcribe_with_whisper(audio_file: str) -> dict:
    """使用本地 Whisper 转录"""
    try:
        import whisper
        print(f"   🖥️ 使用本地 Whisper 转录 (模型：{WHISPER_MODEL})...")
        
        model = whisper.load_model(WHISPER_MODEL)
        result = model.transcribe(audio_file, language='zh')
        
        return {
            'success': True,
            'text': result.get('text', ''),
            'segments': result.get('segments', [])
        }
    except ImportError:
        return {
            'success': False,
            'error': "本地 Whisper 未安装，运行：pip install openai-whisper"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Whisper 转录失败：{str(e)}"
        }


def segments_to_vtt(segments: list, output_file: str):
    """将转录片段转换为 VTT 字幕格式"""
    def format_time(seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("WEBVTT\n\n")
        for i, seg in enumerate(segments, 1):
            start = format_time(seg.get('start', 0))
            end = format_time(seg.get('end', 0))
            text = seg.get('text', '').strip()
            if text:
                f.write(f"{i}\n{start} --> {end}\n{text}\n\n")


def main():
    if len(sys.argv) < 2:
        print("用法：python3 transcribe-audio.py <音频文件> [输出字幕文件]")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else audio_file.rsplit('.', 1)[0] + '.vtt'
    
    if not os.path.exists(audio_file):
        print(f"❌ 音频文件不存在：{audio_file}")
        sys.exit(1)
    
    print("=" * 50)
    print("🎤 语音转录 (Plan B)")
    print("=" * 50)
    print()
    
    # 选择转录方式：优先 Groq，失败则使用硅基流动
    result = {'success': False, 'error': '未尝试'}
    
    if USE_LOCAL_WHISPER:
        # 强制使用本地 Whisper
        print("🖥️ 使用本地 Whisper")
        result = transcribe_with_whisper(audio_file)
    else:
        # 优先尝试 Groq API
        if GROQ_API_KEY:
            print("📡 尝试 Groq API (首选)...")
            result = transcribe_with_groq(audio_file)
            
            if not result['success']:
                print(f"   ⚠️  Groq 失败：{result['error']}")
        
        # Groq 失败则尝试硅基流动
        if not result['success'] and SILICONFLOW_API_KEY:
            print("📡 尝试硅基流动 API (备用)...")
            result = transcribe_with_siliconflow(audio_file)
            
            if not result['success']:
                print(f"   ⚠️  硅基流动失败：{result['error']}")
        
        # 都失败则尝试本地 Whisper
        if not result['success']:
            print("🖥️ 尝试本地 Whisper (最后手段)...")
            result = transcribe_with_whisper(audio_file)
    
    if not result['success']:
        print(f"❌ 转录失败：{result['error']}")
        print("\n💡 提示：请配置以下任一 API Key：")
        print("   - GROQ_API_KEY (Groq API)")
        print("   - SILICONFLOW_API_KEY 或 API_KEY (硅基流动)")
        print("   - 或安装本地 Whisper: pip install openai-whisper")
        sys.exit(1)
    
    print(f"   ✅ 转录完成")
    print(f"   文本长度：{len(result['text'])} 字符")
    print(f"   片段数量：{len(result['segments'])}")
    
    # 保存 VTT 字幕
    if result['segments']:
        segments_to_vtt(result['segments'], output_file)
        print(f"   ✅ 字幕已保存：{output_file}")
    else:
        # 无时间戳，保存纯文本
        text_file = output_file.rsplit('.', 1)[0] + '.txt'
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(result['text'])
        print(f"   ✅ 文本已保存：{text_file}")
    
    print()
    print("=" * 50)
    print("✨ 转录完成！")
    print("=" * 50)


if __name__ == '__main__':
    main()
