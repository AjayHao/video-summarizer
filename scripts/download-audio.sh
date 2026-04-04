#!/bin/bash
# download-audio.sh - Plan B: 下载音频用于语音转录
# 用法：./download-audio.sh <视频 URL> [输出文件]

set -e

VIDEO_URL="$1"
OUTPUT_FILE="${2:-/tmp/audio.mp3}"

echo "🎵 下载音频 (Plan B)..."

# 检测平台
detect_platform() {
    if [[ "$VIDEO_URL" =~ (xiaohongshu\.com|xhslink\.com) ]]; then
        echo "xhs"
    elif [[ "$VIDEO_URL" =~ (douyin\.com|iesdouyin\.com) ]]; then
        echo "douyin"
    else
        echo "other"
    fi
}

PLATFORM=$(detect_platform)

# 尝试 1: 根据平台选择最佳格式
echo "   尝试 1/3: 下载分离音轨..."
if [[ "$PLATFORM" == "xhs" || "$PLATFORM" == "douyin" ]]; then
    # 小红书/抖音：使用 best 格式（这些平台可能没有单独的音频流）
    yt-dlp -f "best" -x --audio-format mp3 -o "$OUTPUT_FILE" "$VIDEO_URL" 2>&1 && \
        [[ -f "$OUTPUT_FILE" ]] && { echo "   ✅ 成功"; exit 0; }
else
    # 其他平台：优先音频流
    yt-dlp -f "bestaudio" -x --audio-format mp3 -o "$OUTPUT_FILE" "$VIDEO_URL" 2>&1 && \
        [[ -f "$OUTPUT_FILE" ]] && { echo "   ✅ 成功"; exit 0; }
fi
rm -f "$OUTPUT_FILE" 2>/dev/null

# 尝试 2: 下载视频并提取音频（通用降级）
echo "   尝试 2/3: 下载视频提取音频..."
TEMP_VIDEO="/tmp/video_temp_$$"
if [[ "$PLATFORM" == "xhs" || "$PLATFORM" == "douyin" ]]; then
    # 小红书/抖音：不限制高度，使用最佳视频
    yt-dlp -f "best" -o "$TEMP_VIDEO.mp4" "$VIDEO_URL" 2>&1 && \
        ffmpeg -i "$TEMP_VIDEO.mp4" -vn -acodec libmp3lame -ab 128k "$OUTPUT_FILE" -y 2>/dev/null && {
            rm -f "$TEMP_VIDEO.mp4"
            [[ -f "$OUTPUT_FILE" ]] && { echo "   ✅ 成功"; exit 0; }
        }
else
    # 其他平台：限制高度以加快下载
    yt-dlp -f "best[height<=480]" -o "$TEMP_VIDEO.mp4" "$VIDEO_URL" 2>&1 && \
        ffmpeg -i "$TEMP_VIDEO.mp4" -vn -acodec libmp3lame -ab 128k "$OUTPUT_FILE" -y 2>/dev/null && {
            rm -f "$TEMP_VIDEO.mp4"
            [[ -f "$OUTPUT_FILE" ]] && { echo "   ✅ 成功"; exit 0; }
        }
fi
rm -f "$TEMP_VIDEO.mp4" 2>/dev/null

# 尝试 3: 强制下载（最后手段）
echo "   尝试 3/3: 强制下载..."
if yt-dlp --format-sort "res:desc" -o "$TEMP_VIDEO.mp4" "$VIDEO_URL" 2>&1; then
    ffmpeg -i "$TEMP_VIDEO.mp4" -vn -acodec libmp3lame -ab 128k "$OUTPUT_FILE" -y 2>/dev/null && {
        rm -f "$TEMP_VIDEO.mp4"
        [[ -f "$OUTPUT_FILE" ]] && { echo "   ✅ 成功"; exit 0; }
    }
fi
rm -f "$TEMP_VIDEO.mp4" 2>/dev/null

echo "   ❌ 音频下载失败"
exit 1
