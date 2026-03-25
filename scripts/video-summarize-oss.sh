#!/bin/bash
# video-summarize.sh - 完整的视频总结生成流程（Plan A 完整版 + 阿里云 OSS 图床）
# 用法：./video-summarize.sh <视频 URL> [输出目录] [cookies 文件]

set -e

VIDEO_URL="$1"
OUTPUT_DIR="${2:-/tmp/video-summarizer}"
COOKIES_FILE="${3:-$HOME/.cookies/bilibili_cookies.txt}"

# 检查 OSS 配置
OSS_UPLOAD_SCRIPT="$HOME/.openclaw/skills/video-summarizer/scripts/upload-to-oss.py"
if [[ -f "$OSS_UPLOAD_SCRIPT" ]]; then
    ENABLE_OSS=true
    echo "📦 阿里云 OSS 图床已启用"
else
    ENABLE_OSS=false
    echo "⚠️  阿里云 OSS 图床未启用（截图将保存在本地）"
fi

mkdir -p "$OUTPUT_DIR"

echo "========================================"
echo "🎬 Video Summarizer v1.4 (Plan A + OSS)"
echo "========================================"
echo ""

# ==================== Step 1: 获取元数据 ====================
echo "📥 Step 1/6: 获取视频元数据..."

yt-dlp --dump-json "$VIDEO_URL" > "$OUTPUT_DIR/metadata.json" 2>/dev/null

# 使用 python 解析 JSON（更可靠）
TITLE=$(python3 -c "import json; print(json.load(open('$OUTPUT_DIR/metadata.json'))['title'])" 2>/dev/null || echo "Unknown")
UPLOADER=$(python3 -c "import json; print(json.load(open('$OUTPUT_DIR/metadata.json'))['uploader'])" 2>/dev/null || echo "Unknown")
DURATION=$(python3 -c "import json; print(json.load(open('$OUTPUT_DIR/metadata.json'))['duration_string'])" 2>/dev/null || echo "Unknown")
DURATION_SEC=$(python3 -c "import json: print(int(json.load(open('$OUTPUT_DIR/metadata.json'))['duration']))" 2>/dev/null || echo "0")
THUMBNAIL=$(python3 -c "import json; print(json.load(open('$OUTPUT_DIR/metadata.json'))['thumbnail'])" 2>/dev/null || echo "")

echo "✅ 元数据获取完成"
echo "   标题：$TITLE"
echo "   UP 主：$UPLOADER"
echo "   时长：$DURATION ($DURATION_SEC 秒)"
echo ""

# ==================== Step 2: 尝试下载字幕 ====================
echo "📝 Step 2/6: 尝试下载字幕..."

SUBTITLE_FILE=""
SUBTITLE_SOURCE=""

# 尝试 1: 用 Cookies 下载官方字幕
if [[ -f "$COOKIES_FILE" ]]; then
    echo "   尝试使用 Cookies 下载官方字幕..."
    yt-dlp --cookies "$COOKIES_FILE" \
           --write-sub --write-auto-sub \
           --sub-lang "ai-zh,zh-Hans,zh,en" \
           --skip-download \
           --convert-subs vtt \
           -o "$OUTPUT_DIR/video" "$VIDEO_URL" 2>/dev/null || true
    
    SUBTITLE_FILE=$(find "$OUTPUT_DIR" -name "*.vtt" 2>/dev/null | head -1)
    if [[ -n "$SUBTITLE_FILE" && -s "$SUBTITLE_FILE" ]]; then
        SUBTITLE_SOURCE="官方字幕 (B 站 AI)"
        echo "   ✅ 官方字幕下载成功！"
        echo "   文件：$SUBTITLE_FILE"
    fi
fi

# 尝试 2: 无 Cookies 下载自动字幕
if [[ -z "$SUBTITLE_FILE" ]]; then
    echo "   尝试下载自动字幕（无需登录）..."
    yt-dlp --write-auto-sub \
           --sub-lang "zh-Hans,zh,en" \
           --skip-download \
           --convert-subs vtt \
           -o "$OUTPUT_DIR/video" "$VIDEO_URL" 2>/dev/null || true
    
    SUBTITLE_FILE=$(find "$OUTPUT_DIR" -name "*.vtt" 2>/dev/null | head -1)
    if [[ -n "$SUBTITLE_FILE" && -s "$SUBTITLE_FILE" ]]; then
        SUBTITLE_SOURCE="自动字幕 (平台)"
        echo "   ✅ 自动字幕下载成功！"
        echo "   文件：$SUBTITLE_FILE"
    fi
fi

# Plan B: 语音转录（暂不启用，提示用户）
if [[ -z "$SUBTITLE_FILE" ]]; then
    echo "   ⚠️  未找到可用字幕"
    echo "   ℹ️  Plan B 语音转录功能待启用（需安装 Whisper）"
    echo "   ❌ 字幕获取失败，无法继续"
    exit 1
fi

echo ""
echo "✅ 字幕来源：$SUBTITLE_SOURCE"
echo ""

# ==================== Step 3: 分析字幕内容 ====================
echo "🧠 Step 3/6: 分析字幕内容..."

# 提取字幕文本（去除时间戳）
awk '
    /^WEBVTT/ { next }
    /^[0-9]/ { next }
    /^$/ { next }
    /-->/ { next }
    { print }
' "$SUBTITLE_FILE" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | grep -v "^$" > "$OUTPUT_DIR/transcript.txt"

WORD_COUNT=$(wc -w < "$OUTPUT_DIR/transcript.txt")
LINE_COUNT=$(wc -l < "$OUTPUT_DIR/transcript.txt")

if [[ $WORD_COUNT -eq 0 ]]; then
    echo "   ⚠️  字幕文本为空，检查字幕文件"
    exit 1
fi

echo "   字幕行数：$LINE_COUNT"
echo "   字幕字数：$WORD_COUNT"
echo "   ✅ 字幕文本提取完成"
echo ""

# ==================== Step 4: 下载视频（必须成功） ====================
echo "📥 Step 4/6: 下载视频（用于截图）..."

VIDEO_FILE="$OUTPUT_DIR/video.mp4"
MAX_RETRIES=3
RETRY_COUNT=0
DOWNLOAD_SUCCESS=false

while [[ $RETRY_COUNT -lt $MAX_RETRIES && "$DOWNLOAD_SUCCESS" == "false" ]]; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   尝试下载视频 (第 $RETRY_COUNT/$MAX_RETRIES 次)..."
    
    yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
           --merge-output-format mp4 \
           -o "$VIDEO_FILE" "$VIDEO_URL" 2>&1 && DOWNLOAD_SUCCESS=true || {
        echo "   ⚠️  下载失败，准备重试..."
        rm -f "$VIDEO_FILE"* 2>/dev/null
    }
done

if [[ "$DOWNLOAD_SUCCESS" == "true" && -f "$VIDEO_FILE" ]]; then
    VIDEO_SIZE=$(ls -lh "$VIDEO_FILE" | awk '{print $5}')
    echo "   ✅ 视频下载成功！($VIDEO_SIZE)"
else
    echo "   ⚠️  标准下载失败，尝试降级模式..."
    yt-dlp -f "best" \
           --merge-output-format mp4 \
           -o "$VIDEO_FILE" "$VIDEO_URL" 2>&1 && {
        echo "   ✅ 降级模式下载成功！"
    } || {
        echo "   ❌ 视频下载失败，无法继续"
        exit 1
    }
fi
echo ""

# ==================== Step 5: 智能截图 ====================
echo "🎬 Step 5/6: 智能截取视频帧..."

if ! ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO_FILE" > /dev/null 2>&1; then
    echo "   ❌ 视频文件损坏，无法截图"
    exit 1
fi

# 计算截图点
if [[ $DURATION_SEC -lt 120 ]]; then
    SCREENSHOTS=("00:00:02" "00:00:30" "00:01:00")
elif [[ $DURATION_SEC -lt 300 ]]; then
    SCREENSHOTS=("00:00:02" "00:01:00" "00:02:00" "00:03:00" "00:04:00")
else
    INTERVAL=$((DURATION_SEC / 8))
    SCREENSHOTS=()
    for i in {1..7}; do
        TIME=$((INTERVAL * i))
        HOURS=$((TIME / 3600))
        MINS=$(((TIME % 3600) / 60))
        SECS=$((TIME % 60))
        SCREENSHOTS+=($(printf "%02d:%02d:%02d" $HOURS $MINS $SECS))
    done
fi

mkdir -p "$OUTPUT_DIR/screenshots"
SUCCESS_COUNT=0

for i in "${!SCREENSHOTS[@]}"; do
    TIME="${SCREENSHOTS[$i]}"
    OUTPUT="$OUTPUT_DIR/screenshots/screenshot_$(printf "%02d" $((i+1))).jpg"
    
    if ffmpeg -ss "$TIME" -i "$VIDEO_FILE" -vframes 1 -update 1 -q:v 2 "$OUTPUT" -y 2>/dev/null; then
        echo "   📸 截图 $((i+1)): $TIME → $(basename $OUTPUT)"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "   ⚠️  截图 $((i+1)) 失败：$TIME"
    fi
done

if [[ $SUCCESS_COUNT -eq 0 ]]; then
    echo "   ❌ 所有截图失败，检查视频文件"
    exit 1
fi

echo "   ✅ 截图完成 ($SUCCESS_COUNT/${#SCREENSHOTS[@]} 张)"
echo ""

# ==================== Step 5.5: 上传截图到阿里云 OSS ====================
OSS_SCREENSHOT_URLS=()
if [[ "$ENABLE_OSS" == "true" && $SUCCESS_COUNT -gt 0 ]]; then
    echo "☁️  上传截图到阿里云 OSS..."
    
    # 生成唯一的上传前缀（使用时间戳）
    UPLOAD_PREFIX="screenshots/$(date +%Y%m%d_%H%M%S)/"
    
    # 批量上传
    while IFS= read -r line; do
        if [[ "$line" =~ ^📎.*https:// ]]; then
            URL=$(echo "$line" | sed 's/.*- //')
            OSS_SCREENSHOT_URLS+=("$URL")
        fi
    done < <(python3 "$OSS_UPLOAD_SCRIPT" batch "$OUTPUT_DIR/screenshots" --prefix "$UPLOAD_PREFIX" 2>&1)
    
    if [[ ${#OSS_SCREENSHOT_URLS[@]} -gt 0 ]]; then
        echo "   ✅ 上传成功 (${#OSS_SCREENSHOT_URLS[@]} 张)"
    else
        echo "   ⚠️  上传失败，使用本地路径"
    fi
    echo ""
fi

# ==================== Step 6: 生成总结草稿 ====================
echo "📝 Step 6/6: 生成结构化总结..."

# 构建截图 Markdown
SCREENSHOT_MD=""
if [[ ${#OSS_SCREENSHOT_URLS[@]} -gt 0 ]]; then
    for url in "${OSS_SCREENSHOT_URLS[@]}"; do
        SCREENSHOT_MD+="![]($url)"$'\n\n'
    done
else
    SCREENSHOT_MD="截图已保存到本地目录：\`$OUTPUT_DIR/screenshots/\`\n\n"
fi

cat > "$OUTPUT_DIR/summary.md" << EOF
# $TITLE

**Tags:** \`视频总结\` \`AI\` \`教程\`

**Status:** ✅ 已完成

**Author:** $UPLOADER

**Cover:**
![视频封面]($THUMBNAIL)

---

## 📝 Note

*待 AI 生成概述*

---

## 📺 视频信息

**链接:** $VIDEO_URL
**时长:** $DURATION
**UP 主:** $UPLOADER
**字幕:** $SUBTITLE_SOURCE

---

## 🎯 核心要点

*待 AI 分析字幕内容后生成*

---

## 📚 关键概念

*待 AI 提取*

---

## 🎬 视频帧截图

$SCREENSHOT_MD
---

## 💡 总结

*待 AI 生成最终总结*

---

*生成时间：$(date +%Y-%m-%d)*
*技能版本：video-summarizer v1.4 (Plan A + OSS)*
*字幕来源：$SUBTITLE_SOURCE*
*字幕字数：$WORD_COUNT*
EOF

echo "   ✅ 总结草稿生成完成"
echo "   文件：$OUTPUT_DIR/summary.md"
echo ""

# ==================== 完成 ====================
echo "========================================"
echo "✅ Plan A 流程完成！"
echo "========================================"
echo ""
echo "输出目录：$OUTPUT_DIR"
echo ""
echo "文件列表:"
ls -lh "$OUTPUT_DIR"
echo ""
if [[ "$ENABLE_OSS" == "true" ]]; then
    echo "截图已上传到阿里云 OSS:"
    for url in "${OSS_SCREENSHOT_URLS[@]}"; do
        echo "  - $url"
    done
    echo ""
else
    echo "截图目录:"
    ls -lh "$OUTPUT_DIR/screenshots/"
    echo ""
fi

# ==================== Step 7: AI 分析生成完整总结 ====================
echo "🧠 Step 7/7: AI 智能分析生成完整总结..."

AI_SUMMARY_FILE="$OUTPUT_DIR/summary-ai.md"
if [[ -f "$AI_SUMMARY_FILE" ]]; then
    echo "   ℹ️  AI 总结已存在，跳过"
else
    python3 "$HOME/.openclaw/skills/video-summarizer/scripts/analyze-subtitles-ai.py" \
        "$SUBTITLE_FILE" \
        "$OUTPUT_DIR/metadata.json" \
        "$AI_SUMMARY_FILE" 2>&1 | grep -E "(✅|❌|🤖)" || true
fi

if [[ -f "$AI_SUMMARY_FILE" ]]; then
    echo "   ✅ AI 分析完成：$AI_SUMMARY_FILE"
    FINAL_SUMMARY="$AI_SUMMARY_FILE"
else
    echo "   ⚠️  AI 分析失败，使用基础版本"
    FINAL_SUMMARY="$OUTPUT_DIR/summary.md"
fi

echo ""

# ==================== Step 8: 生成推送预览 ====================
echo "📤 Step 8/7: 准备推送预览..."

# 提取关键信息用于推送
PUSH_TITLE=$(grep "^# " "$FINAL_SUMMARY" | sed 's/^# //')
PUSH_TAGS=$(grep "\*\*Tags:\*\*" "$FINAL_SUMMARY" | sed 's/.*Tags:\*\* //')
PUSH_AUTHOR=$(grep "\*\*Author:\*\*" "$FINAL_SUMMARY" | sed 's/.*Author:\*\* //')
PUSH_VIDEO_URL=$(grep "\*\*链接:\*\*" "$FINAL_SUMMARY" | sed 's/.*链接:\*\* //')
PUSH_NOTE=$(sed -n '/## 📝 Note/,/---/p' "$FINAL_SUMMARY" | grep -v "## 📝 Note" | grep -v "^---$" | head -3)

echo ""
echo "========================================"
echo "✅ Plan A 完整流程完成！"
echo "========================================"
echo ""
echo "📎 推送预览:"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎬 视频总结已完成！"
echo ""
echo "📝 **$PUSH_TITLE**"
echo ""
echo "$PUSH_TAGS"
echo "👤 UP 主：$PUSH_AUTHOR"
echo "🔗 $PUSH_VIDEO_URL"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 **概述**"
echo "$PUSH_NOTE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ 处理完成！请老大审阅："
echo "  - 查看完整总结：$FINAL_SUMMARY"
echo "  - 回复'推送到 Notion' → 推送到 Notion"
echo "  - 回复'修改 XXX' → 根据意见修改"
echo "  - 回复'取消' → 放弃推送"
echo ""
echo "========================================"
echo ""

# 保存推送预览
cat > "$OUTPUT_DIR/PUSH_PREVIEW.txt" << EOF
━━━━━━━━━━━━━━━━━━━━━━━━
🎬 视频总结已完成！

📝 **$PUSH_TITLE**

$PUSH_TAGS
👤 UP 主：$PUSH_AUTHOR
🔗 $PUSH_VIDEO_URL

━━━━━━━━━━━━━━━━━━━━━━━━

📝 **概述**
$PUSH_NOTE

━━━━━━━━━━━━━━━━━━━━━━━━

✅ 处理完成！请老大审阅后回复：
  - "推送到 Notion" → 推送到 Notion
  - "修改 XXX" → 根据意见修改
  - "取消" → 放弃推送
EOF

echo "📋 推送预览已保存：$OUTPUT_DIR/PUSH_PREVIEW.txt"
echo ""
echo "下一步操作:"
echo "  1. 老大审阅上方预览"
echo "  2. 回复确认指令"
echo "  3. 执行推送："
echo "     python3 ~/.openclaw/skills/video-summarizer/scripts/push-to-notion.py \\"
echo "         $FINAL_SUMMARY \\"
echo "         [Notion Database ID]"
echo ""
