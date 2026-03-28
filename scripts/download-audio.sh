#!/bin/bash
# download-audio.sh - Plan B: 下载音频用于语音转录
# 用法：./download-audio.sh <视频 URL> [输出文件]

set -e

VIDEO_URL="$1"
OUTPUT_FILE="${2:-/tmp/audio.mp3}"

echo "🎵 下载音频 (Plan B)..."

# 尝试 1: 直接下载分离音轨（最快）
echo "   尝试 1/3: 下载分离音轨..."
if yt-dlp -f "bestaudio" -x --audio-format mp3 -o "$OUTPUT_FILE" "$VIDEO_URL" 2>&1; then
    [[ -f "$OUTPUT_FILE" ]] && { echo "   ✅ 成功"; exit 0; }
fi

# 尝试 2: 下载并转换（重试 1 次）
echo "   尝试 2/3: 下载并转换..."
for i in 1 2; do
    if yt-dlp -f "bestaudio" -x --audio-format mp3 --postprocessor-args "ffmpeg:-b:a 128k" -o "$OUTPUT_FILE" "$VIDEO_URL" 2>&1; then
        [[ -f "$OUTPUT_FILE" ]] && { echo "   ✅ 成功"; exit 0; }
    fi
    rm -f "$OUTPUT_FILE" 2>/dev/null
done

# 尝试 3: 下载视频并提取音频（降级）
echo "   尝试 3/3: 下载视频提取音频..."
TEMP_VIDEO="/tmp/video_temp_$$"
if yt-dlp -f "best[height<=480]" -o "$TEMP_VIDEO.mp4" "$VIDEO_URL" 2>&1; then
    ffmpeg -i "$TEMP_VIDEO.mp4" -vn -acodec libmp3lame -ab 128k "$OUTPUT_FILE" -y 2>/dev/null && {
        rm -f "$TEMP_VIDEO.mp4"
        [[ -f "$OUTPUT_FILE" ]] && { echo "   ✅ 成功"; exit 0; }
    }
    rm -f "$TEMP_VIDEO.mp4" 2>/dev/null
fi

echo "   ❌ 音频下载失败"
exit 1
