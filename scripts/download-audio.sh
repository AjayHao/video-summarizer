#!/bin/bash
# download-audio.sh - 下载音频轨道（带重试和降级机制）
# 用法：./download-audio.sh <视频 URL> [输出文件]

set -e

VIDEO_URL="$1"
OUTPUT_FILE="${2:-/tmp/audio.mp3}"

echo "🎵 下载音频轨道..."
echo "   目标：$OUTPUT_FILE"
echo ""

# 尝试 1: 直接下载分离音频轨道（最佳）
echo "   尝试 1/3: 直接下载分离音频轨道..."
if yt-dlp -f "bestaudio/best" \
          --audio-format mp3 \
          -o "$OUTPUT_FILE" "$VIDEO_URL" 2>/dev/null; then
    if [[ -f "$OUTPUT_FILE" ]]; then
        SIZE=$(ls -lh "$OUTPUT_FILE" | awk '{print $5}')
        echo "   ✅ 成功！(分离音轨，$SIZE)"
        exit 0
    fi
fi
echo "   ⚠️  失败，尝试降级方案..."

# 尝试 2: 下载音频并转换（重试 1）
echo ""
echo "   尝试 2/3: 下载并转换音频 (重试 1)..."
if yt-dlp -x --audio-format mp3 --audio-quality 128K \
          -o "$OUTPUT_FILE" "$VIDEO_URL" 2>/dev/null; then
    if [[ -f "$OUTPUT_FILE" ]]; then
        SIZE=$(ls -lh "$OUTPUT_FILE" | awk '{print $5}')
        echo "   ✅ 成功！(转换音频，$SIZE)"
        exit 0
    fi
fi
echo "   ⚠️  失败，尝试最终方案..."

# 尝试 3: 从视频提取（最后手段）
echo ""
echo "   尝试 3/3: 下载视频并提取音频 (降级模式)..."
TEMP_VIDEO="/tmp/temp_video_$$"
if yt-dlp -f "bestvideo[height<=480]+bestaudio/best[height<=480]" \
          -o "$TEMP_VIDEO.mp4" "$VIDEO_URL" 2>/dev/null; then
    
    echo "   从视频中提取音频..."
    ffmpeg -i "$TEMP_VIDEO.mp4" -vn -acodec libmp3lame -ab 128k "$OUTPUT_FILE" -y 2>/dev/null
    
    # 清理临时文件
    rm -f "$TEMP_VIDEO.mp4"
    
    if [[ -f "$OUTPUT_FILE" ]]; then
        SIZE=$(ls -lh "$OUTPUT_FILE" | awk '{print $5}')
        echo "   ✅ 成功！(视频提取，$SIZE)"
        exit 0
    fi
fi

# 全部失败
echo ""
echo "   ❌ 所有尝试失败"
rm -f "$OUTPUT_FILE" 2>/dev/null
exit 1
