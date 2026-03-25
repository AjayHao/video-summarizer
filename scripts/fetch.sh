#!/bin/bash
# fetch.sh - 获取视频元数据、字幕和截图
# 用法：./fetch.sh <视频 URL> [输出目录] [cookies 文件]

set -e

VIDEO_URL="$1"
OUTPUT_DIR="${2:-/tmp/video-summarizer}"
COOKIES_FILE="${3:-$HOME/.cookies/bilibili_cookies.txt}"

mkdir -p "$OUTPUT_DIR"

echo "📥 获取视频元数据..."

# 检测视频平台
if [[ "$VIDEO_URL" == *"bilibili.com"* ]]; then
    PLATFORM="bilibili"
elif [[ "$VIDEO_URL" == *"youtube.com"* ]] || [[ "$VIDEO_URL" == *"youtu.be"* ]]; then
    PLATFORM="youtube"
else
    echo "⚠️  未知平台，尝试通用模式..."
    PLATFORM="generic"
fi

# 使用 yt-dlp 获取元数据
yt-dlp --dump-json "$VIDEO_URL" > "$OUTPUT_DIR/metadata.json" 2>/dev/null

# 提取关键信息
TITLE=$(grep -o '"title":"[^"]*"' "$OUTPUT_DIR/metadata.json" | head -1 | cut -d'"' -f4)
UPLOADER=$(grep -o '"uploader":"[^"]*"' "$OUTPUT_DIR/metadata.json" | head -1 | cut -d'"' -f4)
DURATION=$(grep -o '"duration_string":"[^"]*"' "$OUTPUT_DIR/metadata.json" | head -1 | cut -d'"' -f4)
THUMBNAIL=$(grep -o '"thumbnail":"[^"]*"' "$OUTPUT_DIR/metadata.json" | head -1 | cut -d'"' -f4)
UPLOAD_DATE=$(grep -o '"upload_date":"[^"]*"' "$OUTPUT_DIR/metadata.json" | head -1 | cut -d'"' -f4)
VIEW_COUNT=$(grep -o '"view_count":[0-9]*' "$OUTPUT_DIR/metadata.json" | head -1 | cut -d':' -f2)
LIKE_COUNT=$(grep -o '"like_count":[0-9]*' "$OUTPUT_DIR/metadata.json" | head -1 | cut -d':' -f2)

echo "✅ 元数据获取完成"
echo ""
echo "标题：$TITLE"
echo "UP 主：$UPLOADER"
echo "时长：$DURATION"
echo "上传日期：$UPLOAD_DATE"
echo "播放：$VIEW_COUNT"
echo "点赞：$LIKE_COUNT"
echo ""

# 下载字幕
echo "📝 下载字幕..."
if [[ -f "$COOKIES_FILE" ]]; then
    echo "使用 Cookies: $COOKIES_FILE"
    yt-dlp --cookies "$COOKIES_FILE" \
           --write-sub --write-auto-sub \
           --sub-lang "ai-zh,zh-Hans,zh,en" \
           --skip-download \
           --convert-subs vtt \
           -o "$OUTPUT_DIR/video" "$VIDEO_URL" 2>/dev/null || echo "⚠️  无可用字幕"
else
    echo "⚠️  未找到 Cookies 文件，尝试下载自动字幕..."
    yt-dlp --write-auto-sub \
           --sub-lang "zh-Hans,zh,en" \
           --skip-download \
           --convert-subs vtt \
           -o "$OUTPUT_DIR/video" "$VIDEO_URL" 2>/dev/null || echo "⚠️  无可用字幕"
fi

# 查找字幕文件
SUBTITLE_FILE=$(find "$OUTPUT_DIR" -name "*.vtt" 2>/dev/null | head -1)
if [[ -n "$SUBTITLE_FILE" ]]; then
    echo "✅ 字幕文件：$SUBTITLE_FILE"
else
    echo "⚠️  未找到字幕文件"
fi

# 提取视频 ID 用于截图
VIDEO_ID=$(grep -o '"id":"[^"]*"' "$OUTPUT_DIR/metadata.json" | head -1 | cut -d'"' -f4)
echo "$VIDEO_ID" > "$OUTPUT_DIR/video_id.txt"

echo ""
echo "✅ 完成！输出目录：$OUTPUT_DIR"
echo "   元数据：$OUTPUT_DIR/metadata.json"
echo "   视频 ID: $VIDEO_ID"
echo "   字幕：$SUBTITLE_FILE"
