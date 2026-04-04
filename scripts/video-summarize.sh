#!/bin/bash
# video-summarize.sh - 视频总结生成完整流程 v0.1.2
# 用法：./video-summarize.sh <视频 URL> [输出目录] [cookies 文件] [选项]

set -e

# ============== 错误处理与日志 ==============

# 日志级别函数
log_info() { echo "ℹ️  $*"; }
log_warn() { echo "⚠️  $*"; }
log_error() { echo "❌ $*"; }

# 错误捕获 trap
ERROR_LOG=""
cleanup_on_error() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_error "脚本执行失败 (退出码：$exit_code)"
        if [[ -n "$ERROR_LOG" && -f "$ERROR_LOG" ]]; then
            log_error "详细错误日志：$ERROR_LOG"
            [[ "$VERBOSE" == "true" ]] && tail -20 "$ERROR_LOG"
        fi
    fi
    exit $exit_code
}
trap cleanup_on_error ERR

# 平台标识映射（统一小写）
# bilibili, xhs, douyin, youtube, wxvideo

# 解析参数
VIDEO_URL=""
OUTPUT_DIR=""
USER_SPECIFIED_OUTPUT="false"  # 标记用户是否手动指定了输出目录
COOKIES_FILE="$HOME/.cookies/bilibili_cookies.txt"
VERBOSE="false"
KEEP_VIDEO="false"
AUTO_PUSH="false"
RESUME="false"

for arg in "$@"; do
    case $arg in
        --verbose|-v)
            VERBOSE="true"
            ;;
        --keep-video)
            KEEP_VIDEO="true"
            ;;
        --push|--auto-push)
            AUTO_PUSH="true"
            ;;
        --resume)
            RESUME="true"
            ;;
        *)
            if [[ -z "$VIDEO_URL" ]]; then
                VIDEO_URL="$arg"
            elif [[ "$USER_SPECIFIED_OUTPUT" == "false" ]]; then
                OUTPUT_DIR="$arg"
                USER_SPECIFIED_OUTPUT="true"
            elif [[ "$COOKIES_FILE" == "$HOME/.cookies/bilibili_cookies.txt" ]]; then
                COOKIES_FILE="$arg"
            fi
            ;;
    esac
done

if [[ -z "$VIDEO_URL" ]]; then
    echo "用法：./video-summarize.sh <视频 URL> [输出目录] [cookies 文件] [选项]"
    echo ""
    echo "选项:"
    echo "  --verbose, -v      显示详细日志（包括错误信息）"
    echo "  --keep-video       保留视频/音频文件（默认清理）"
    echo "  --push, --auto-push  完成后自动推送到 Notion"
    echo "  --resume           从中断点恢复（检测进度文件）"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ============== 平台识别与输出目录生成 ==============

# 提取平台标识
extract_platform() {
    local url="$1"
    
    # B 站：bilibili.com 或 b23.tv
    if [[ "$url" =~ (bilibili\.com|b23\.tv) ]]; then
        echo "bilibili"
        return
    fi
    
    # 小红书：xiaohongshu.com 或 xhslink.com
    if [[ "$url" =~ (xiaohongshu\.com|xhslink\.com) ]]; then
        echo "xhs"
        return
    fi
    
    # 抖音：douyin.com 或 iesdouyin.com
    if [[ "$url" =~ (douyin\.com|iesdouyin\.com) ]]; then
        echo "douyin"
        return
    fi
    
    # YouTube：youtube.com 或 youtu.be
    if [[ "$url" =~ (youtube\.com|youtu\.be) ]]; then
        echo "youtube"
        return
    fi
    
    # 微信视频：channels.weixin.qq.com
    if [[ "$url" =~ (channels\.weixin\.qq\.com|mp\.weixin\.qq\.com) ]]; then
        echo "wxvideo"
        return
    fi
    
    # 未知平台
    echo "unknown"
}

# 提取视频 ID
extract_video_id() {
    local url="$1"
    local platform="$2"
    
    case "$platform" in
        bilibili)
            # 提取 BV 号或 av 号
            if [[ "$url" =~ (BV[a-zA-Z0-9]+) ]]; then
                echo "${BASH_REMATCH[1]}"
            elif [[ "$url" =~ av([0-9]+) ]]; then
                echo "av${BASH_REMATCH[1]}"
            else
                # 短链：使用路径作为 ID
                local path=$(echo "$url" | sed -E 's|https?://[^/]+/||' | cut -d'?' -f1)
                echo "${path:-b23_shortlink}"
            fi
            ;;
        xhs)
            # 小红书笔记 ID（数字或带字母）
            if [[ "$url" =~ /([a-zA-Z0-9]{10,})(\?|$|\&|/) ]]; then
                echo "${BASH_REMATCH[1]}"
            else
                # 短链：使用路径作为 ID
                local path=$(echo "$url" | sed -E 's|https?://[^/]+/||' | cut -d'?' -f1)
                echo "${path:-xhs_shortlink}"
            fi
            ;;
        douyin)
            # 抖音：提取视频 ID 或使用短链哈希
            if [[ "$url" =~ /video/([0-9]+) ]]; then
                echo "${BASH_REMATCH[1]}"
            elif [[ "$url" =~ /([a-zA-Z0-9_-]{10,})(\?|$) ]]; then
                echo "${BASH_REMATCH[1]}"
            else
                # 短链：使用路径作为 ID
                local path=$(echo "$url" | sed -E 's|https?://[^/]+/||' | cut -d'?' -f1)
                echo "${path:-douyin_shortlink}"
            fi
            ;;
        youtube)
            # YouTube 视频 ID
            if [[ "$url" =~ v=([a-zA-Z0-9_-]+) ]]; then
                echo "${BASH_REMATCH[1]}"
            elif [[ "$url" =~ youtu\.be/([a-zA-Z0-9_-]+) ]]; then
                echo "${BASH_REMATCH[1]}"
            else
                echo "unknown"
            fi
            ;;
        wxvideo)
            # 微信视频号：提取 ID 或使用 URL 哈希
            if [[ "$url" =~ vid=([a-zA-Z0-9]+) ]]; then
                echo "${BASH_REMATCH[1]}"
            else
                # 使用 URL 的 MD5 前 12 位作为标识
                echo "$url" | md5sum | cut -c1-12
            fi
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# 生成输出目录
if [[ "$USER_SPECIFIED_OUTPUT" == "true" ]]; then
    # 用户手动指定了目录，直接使用
    : # OUTPUT_DIR 已设置
else
    # 自动生成：/tmp/video-summarizer/<平台>/<视频 ID>
    PLATFORM=$(extract_platform "$VIDEO_URL")
    VIDEO_ID=$(extract_video_id "$VIDEO_URL" "$PLATFORM")
    OUTPUT_DIR="/tmp/video-summarizer/$PLATFORM/$VIDEO_ID"
fi

mkdir -p "$OUTPUT_DIR"

# 进度文件
PROGRESS_FILE="$OUTPUT_DIR/.progress.json"

echo "📁 输出目录：$OUTPUT_DIR"
echo "🏷️  平台：$PLATFORM | 视频 ID: $VIDEO_ID"
echo ""

# 检查环境变量（自动推送）
if [[ "$AUTO_PUSH" == "true" ]]; then
    if [[ -z "$NOTION_VIDEO_SUMMARY_DATABASE_ID" ]]; then
        NOTION_VIDEO_SUMMARY_DATABASE_ID=$(grep "^NOTION_VIDEO_SUMMARY_DATABASE_ID=" "$HOME/.openclaw/.env" 2>/dev/null | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    fi
fi

[[ "$VERBOSE" == "true" ]] && echo "🔍 详细模式 | "
[[ "$KEEP_VIDEO" == "true" ]] && echo "💾 保留视频 | "
[[ "$AUTO_PUSH" == "true" ]] && echo "📤 自动推送 | "
[[ "$RESUME" == "true" ]] && echo "♻️  恢复模式"
echo ""

# 进度保存函数
save_progress() {
    local step=$1
    local status=$2
    local timestamp=$(date -Iseconds)
    cat > "$PROGRESS_FILE" << EOF
{
  "video_url": "$VIDEO_URL",
  "current_step": "$step",
  "status": "$status",
  "timestamp": "$timestamp",
  "output_dir": "$OUTPUT_DIR"
}
EOF
}

# 检查进度（恢复模式）
check_progress() {
    if [[ "$RESUME" == "true" && -f "$PROGRESS_FILE" ]]; then
        local last_step=$(python3 -c "import json; print(json.load(open('$PROGRESS_FILE')).get('current_step', ''))" 2>/dev/null)
        if [[ -n "$last_step" ]]; then
            echo "♻️  检测到上次运行到：Step $last_step"
            echo "   将跳过已完成的步骤..."
            return 0
        fi
    fi
    return 1
}

echo "🎬 Video Summarizer v0.1.2"
echo ""

# Step 1: 元数据
if check_progress && [[ -f "$OUTPUT_DIR/metadata.json" ]]; then
    echo "⏭️  Step 1 跳过"
else
    echo "📥 Step 1: 元数据..."
    save_progress "1" "running"
    
    if [[ "$VERBOSE" == "true" ]]; then
        yt-dlp --dump-json "$VIDEO_URL" > "$OUTPUT_DIR/metadata.json"
    else
        yt-dlp --dump-json "$VIDEO_URL" > "$OUTPUT_DIR/metadata.json" 2>/dev/null
    fi
    
    TITLE=$(python3 -c "import json; print(json.load(open('$OUTPUT_DIR/metadata.json'))['title'])" 2>/dev/null || echo "Unknown")
    UPLOADER=$(python3 -c "import json; print(json.load(open('$OUTPUT_DIR/metadata.json'))['uploader'])" 2>/dev/null || echo "Unknown")
    DURATION=$(python3 -c "import json; print(json.load(open('$OUTPUT_DIR/metadata.json'))['duration_string'])" 2>/dev/null || echo "Unknown")
    DURATION_SEC=$(python3 -c "import json; print(int(json.load(open('$OUTPUT_DIR/metadata.json'))['duration']))" 2>/dev/null || echo "0")
    THUMBNAIL=$(python3 -c "import json; print(json.load(open('$OUTPUT_DIR/metadata.json'))['thumbnail'])" 2>/dev/null || echo "")
    
    echo "✅ 元数据完成 | 标题：$TITLE | UP 主：$UPLOADER | 时长：$DURATION"
    [[ "$VERBOSE" == "true" ]] && echo "   📄 $OUTPUT_DIR/metadata.json"
    save_progress "1" "done"
fi

# Step 2: 字幕
if check_progress && [[ -n "$(find "$OUTPUT_DIR" -name "*.vtt" 2>/dev/null | head -1)" ]]; then
    echo "⏭️  Step 2 跳过"
    SUBTITLE_FILE=$(find "$OUTPUT_DIR" -name "*.vtt" 2>/dev/null | head -1)
    SUBTITLE_SOURCE="已存在"
else
    echo "📝 Step 2: 字幕..."
    save_progress "2" "running"
    
    SUBTITLE_FILE=""
    SUBTITLE_SOURCE=""
    SUBTITLE_LOG="$OUTPUT_DIR/subtitle_download.log"

# 尝试 1: Cookies + 官方字幕
if [[ -f "$COOKIES_FILE" ]]; then
    log_info "   尝试使用 Cookies 下载官方字幕..."
    if [[ "$VERBOSE" == "true" ]]; then
        yt-dlp --cookies "$COOKIES_FILE" \
               --write-sub --write-auto-sub \
               --sub-lang "ai-zh,zh-Hans,zh,en" \
               --skip-download \
               --convert-subs vtt \
               -o "$OUTPUT_DIR/video" "$VIDEO_URL" 2>&1 | tee -a "$SUBTITLE_LOG" || true
    else
        yt-dlp --cookies "$COOKIES_FILE" \
               --write-sub --write-auto-sub \
               --sub-lang "ai-zh,zh-Hans,zh,en" \
               --skip-download \
               --convert-subs vtt \
               -o "$OUTPUT_DIR/video" "$VIDEO_URL" 2>/dev/null || true
    fi
    
    SUBTITLE_FILE=$(find "$OUTPUT_DIR" -name "*.vtt" 2>/dev/null | head -1)
    [[ -n "$SUBTITLE_FILE" && -s "$SUBTITLE_FILE" ]] && SUBTITLE_SOURCE="官方字幕"
fi

# 尝试 2: 自动字幕
if [[ -z "$SUBTITLE_FILE" ]]; then
    echo "   尝试下载自动字幕..."
    if [[ "$VERBOSE" == "true" ]]; then
        yt-dlp --write-auto-sub \
               --sub-lang "zh-Hans,zh,en" \
               --skip-download \
               --convert-subs vtt \
               -o "$OUTPUT_DIR/video" "$VIDEO_URL" 2>&1 | tee -a "$SUBTITLE_LOG" || true
    else
        yt-dlp --write-auto-sub \
               --sub-lang "zh-Hans,zh,en" \
               --skip-download \
               --convert-subs vtt \
               -o "$OUTPUT_DIR/video" "$VIDEO_URL" 2>/dev/null || true
    fi
    
    SUBTITLE_FILE=$(find "$OUTPUT_DIR" -name "*.vtt" 2>/dev/null | head -1)
    [[ -n "$SUBTITLE_FILE" && -s "$SUBTITLE_FILE" ]] && SUBTITLE_SOURCE="自动字幕"
fi

# Plan B: 语音转录
if [[ -z "$SUBTITLE_FILE" ]]; then
    log_warn "未找到可用字幕，启动 Plan B 语音转录..."
    
    AUDIO_FILE="$OUTPUT_DIR/audio.mp3"
    SUBTITLE_FILE="$OUTPUT_DIR/audio.vtt"
    
    # 下载音频
    "$SCRIPT_DIR/download-audio.sh" "$VIDEO_URL" "$AUDIO_FILE"
    
    # 语音转录
    python3 "$SCRIPT_DIR/transcribe-audio.py" "$AUDIO_FILE" "$SUBTITLE_FILE"
    
    SUBTITLE_SOURCE="语音转录 (Plan B)"
    echo "   ✅ 语音转录完成"
fi

echo "✅ 字幕完成 | 来源：$SUBTITLE_SOURCE"
save_progress "2" "done"
fi

# Step 3: 文本提取
if check_progress && [[ -f "$OUTPUT_DIR/transcript.txt" ]]; then
    echo "⏭️  Step 3 跳过"
    WORD_COUNT=$(wc -w < "$OUTPUT_DIR/transcript.txt")
else
    echo "📝 Step 3: 文本提取..."
    save_progress "3" "running"
    
    awk '/^WEBVTT/{next} /^[0-9]/{next} /^$/{next} /-->/ {next} {print}' "$SUBTITLE_FILE" | \
        sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | grep -v "^$" > "$OUTPUT_DIR/transcript.txt"
    
    WORD_COUNT=$(wc -w < "$OUTPUT_DIR/transcript.txt")
    LINE_COUNT=$(wc -l < "$OUTPUT_DIR/transcript.txt")
    
    if [[ $WORD_COUNT -eq 0 ]]; then
        echo "   ❌ 字幕文本为空"
        exit 1
    fi
    
    echo "✅ 文本提取完成 | $LINE_COUNT 行 | $WORD_COUNT 字"
    save_progress "3" "done"
fi

# Step 4: 视频下载
if check_progress && [[ -f "$OUTPUT_DIR/video.mp4" ]]; then
    echo "⏭️  Step 4 跳过"
    VIDEO_FILE="$OUTPUT_DIR/video.mp4"
else
    echo "📥 Step 4: 视频下载..."
    save_progress "4" "running"
    
    VIDEO_FILE="$OUTPUT_DIR/video.mp4"
    DOWNLOAD_SUCCESS=false
    VIDEO_LOG="$OUTPUT_DIR/video_download.log"

for i in 1 2 3; do
    log_info "   尝试 $i/3..."
    if [[ "$VERBOSE" == "true" ]]; then
        yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
               --merge-output-format mp4 \
               -o "$VIDEO_FILE" "$VIDEO_URL" 2>&1 | tee -a "$VIDEO_LOG" && { DOWNLOAD_SUCCESS=true; break; } || {
            rm -f "$VIDEO_FILE"* 2>/dev/null
        }
    else
        yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
               --merge-output-format mp4 \
               -o "$VIDEO_FILE" "$VIDEO_URL" 2>/dev/null && { DOWNLOAD_SUCCESS=true; break; } || {
            rm -f "$VIDEO_FILE"* 2>/dev/null
        }
    fi
done

if [[ "$DOWNLOAD_SUCCESS" != "true" ]]; then
    echo "   降级尝试..."
    if [[ "$VERBOSE" == "true" ]]; then
        yt-dlp -f "best" --merge-output-format mp4 -o "$VIDEO_FILE" "$VIDEO_URL" 2>&1 | tee -a "$VIDEO_LOG" || {
            echo "   ❌ 视频下载失败"
            exit 1
        }
    else
        yt-dlp -f "best" --merge-output-format mp4 -o "$VIDEO_FILE" "$VIDEO_URL" 2>/dev/null || {
            echo "   ❌ 视频下载失败"
            exit 1
        }
    fi
fi

echo "✅ 视频下载成功 | $(ls -lh "$VIDEO_FILE" | awk '{print $5}')"
    save_progress "4" "done"
fi

# Step 5: AI 分析（先生成 JSON，供截图使用）
if check_progress && [[ -f "$OUTPUT_DIR/ai_result.json" ]]; then
    echo "⏭️  Step 5 跳过（AI 结果已存在）"
else
    echo "🤖 Step 5: AI 分析（生成 JSON）..."
    save_progress "5" "running"
    
    AI_SCRIPT="$SCRIPT_DIR/analyze-subtitles-ai.py"
    AI_JSON_FILE="$OUTPUT_DIR/ai_result.json"
    AI_LOG="$OUTPUT_DIR/ai_analysis.log"
    TEMP_SUMMARY="$OUTPUT_DIR/summary_temp.md"
    
    if [[ -f "$AI_SCRIPT" ]]; then
        if [[ "$VERBOSE" == "true" ]]; then
            python3 "$AI_SCRIPT" "$SUBTITLE_FILE" "$OUTPUT_DIR/metadata.json" "$TEMP_SUMMARY" 2>&1 | tee -a "$AI_LOG"
        else
            python3 "$AI_SCRIPT" "$SUBTITLE_FILE" "$OUTPUT_DIR/metadata.json" "$TEMP_SUMMARY" 2>/dev/null
        fi
        
        if [[ -f "$AI_JSON_FILE" ]]; then
            echo "✅ AI 分析完成 | JSON: $AI_JSON_FILE"
            AI_SUCCESS="true"
        else
            log_warn "AI 分析失败，使用基础版总结（无 AI 分析）"
            [[ "$VERBOSE" == "true" ]] && cat "$AI_LOG" | tail -10
            AI_SUCCESS="false"
            # 创建空的 AI 结果文件，供后续步骤使用
            cat > "$AI_JSON_FILE" << 'AIJSON'
{
  "note": "AI 分析失败，无法生成概述。",
  "key_points": [],
  "concepts": [],
  "warnings": [],
  "summary": "AI 分析失败，无法生成总结。"
}
AIJSON
        fi
    else
        log_warn "AI 脚本不存在，使用基础版总结"
        AI_SUCCESS="false"
    fi
    save_progress "5" "done"
fi

# Step 6: 截图（基于 AI 分析的时间戳）
if check_progress && [[ -d "$OUTPUT_DIR/screenshots" && -n "$(ls -A "$OUTPUT_DIR/screenshots" 2>/dev/null)" ]]; then
    echo "⏭️  Step 6 跳过"
else
    echo "🎬 Step 6: 截图（基于 AI 分析结果）..."
    save_progress "6" "running"
    
    mkdir -p "$OUTPUT_DIR/screenshots"
    
    # 从 AI 分析结果中提取时间戳（核心要点 + 注意事项，支持最多 30 张）
    SCREENSHOT_TIMES=()
    AI_JSON="$OUTPUT_DIR/ai_result.json"
    MAX_SCREENSHOTS=30
    
    if [[ -f "$AI_JSON" ]]; then
        echo "   📊 从 AI 分析结果提取时间戳..."
        # 使用 Python 提取 key_points 和 warnings 中的时间戳
        SCREENSHOT_TIMES=($(python3 << PYEOF
import json
import sys

try:
    with open('$AI_JSON', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    times = []
    # 提取核心要点时间戳（优先）
    for point in data.get('key_points', []):
        time_str = point.get('time', '')
        if time_str:
            times.append(time_str)
    
    # 提取注意事项时间戳
    for warning in data.get('warnings', []):
        time_str = warning.get('time', '')
        if time_str:
            times.append(time_str)
    
    # 去重，限制最多 30 个
    unique_times = list(dict.fromkeys(times))[:$MAX_SCREENSHOTS]
    
    # 如果不足 10 个，用均匀分布补充到 10 个
    if len(unique_times) < 10:
        # 简单均匀分布兜底
        interval = $DURATION_SEC // 11
        for i in range(1, 11):
            t = interval * i
            mm = t // 60
            ss = t % 60
            fallback = f"{mm:02d}:{ss:02d}"
            if fallback not in unique_times:
                unique_times.append(fallback)
            if len(unique_times) >= 10:
                break
    
    for t in unique_times[:$MAX_SCREENSHOTS]:
        print(t)
except Exception as e:
    # AI 结果解析失败，使用均匀分布
    interval = $DURATION_SEC // 11
    for i in range(1, 11):
        t = interval * i
        mm = t // 60
        ss = t % 60
        print(f"{mm:02d}:{ss:02d}")
PYEOF
))
        echo "   ✅ 提取到 ${#SCREENSHOT_TIMES[@]} 个时间点"
    else
        echo "   ⚠️  AI 结果不存在，使用均匀分布兜底"
    fi
    
    # 如果提取失败，使用均匀分布
    if [[ ${#SCREENSHOT_TIMES[@]} -eq 0 ]]; then
        if [[ $DURATION_SEC -lt 120 ]]; then
            SCREENSHOT_TIMES=("00:02" "00:30" "01:00" "01:30" "02:00")
        elif [[ $DURATION_SEC -lt 300 ]]; then
            SCREENSHOT_TIMES=("00:02" "00:30" "01:00" "01:30" "02:00" "02:30" "03:00" "03:30" "04:00" "04:30")
        else
            INTERVAL=$((DURATION_SEC / 11))
            SCREENSHOT_TIMES=()
            for i in {1..10}; do
                T=$((INTERVAL * i))
                SCREENSHOT_TIMES+=($(printf "%02d:%02d" $((T/60)) $((T%60))))
            done
        fi
        echo "   📊 使用均匀分布：${#SCREENSHOT_TIMES[@]} 个时间点"
    fi
    
    # 执行截图
    SUCCESS_COUNT=0
    for i in "${!SCREENSHOT_TIMES[@]}"; do
        TIME="${SCREENSHOT_TIMES[$i]}"
        # 转换为 HH:MM:SS 格式（ffmpeg 需要）
        if [[ "$TIME" =~ ^([0-9]+):([0-9]+)$ ]]; then
            FFMPEG_TIME="00:${BASH_REMATCH[1]}:${BASH_REMATCH[2]}"
        elif [[ "$TIME" =~ ^([0-9]+):([0-9]+):([0-9]+)$ ]]; then
            FFMPEG_TIME="${BASH_REMATCH[1]}:${BASH_REMATCH[2]}:${BASH_REMATCH[3]}"
        else
            FFMPEG_TIME="00:$TIME"
        fi
        
        OUT="$OUTPUT_DIR/screenshots/screenshot_$(printf "%02d" $((i+1))).jpg"
        ffmpeg -ss "$FFMPEG_TIME" -i "$VIDEO_FILE" -vframes 1 -update 1 -q:v 2 "$OUT" -y 2>/dev/null && {
            echo "   📸 $TIME → screenshot_$(printf "%02d" $((i+1))).jpg"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        }
    done
    
    [[ $SUCCESS_COUNT -eq 0 ]] && { echo "❌ 截图失败"; exit 1; }
    echo "✅ 截图完成 | $SUCCESS_COUNT 张"
    
    # 保存截图时间戳（供 Markdown 渲染使用）
    SCREENSHOT_TIMES_FILE="$OUTPUT_DIR/screenshot_times.txt"
    printf '%s\n' "${SCREENSHOT_TIMES[@]}" > "$SCREENSHOT_TIMES_FILE"
    echo "   💾 截图时间戳已保存：$SCREENSHOT_TIMES_FILE"
    
    save_progress "6" "done"
fi

# Step 7: OSS 上传
if check_progress && [[ -f "$OUTPUT_DIR/screenshot_urls.txt" ]]; then
    echo "⏭️  Step 7 跳过"
else
    echo "☁️  Step 7: OSS 上传..."
    save_progress "7" "running"
    
    OSS_SCRIPT="$SCRIPT_DIR/upload-to-oss.py"
    OSS_URLS_FILE="$OUTPUT_DIR/screenshot_urls.txt"
    OSS_LOG_FILE="$OUTPUT_DIR/oss_upload.log"

if [[ -f "$OSS_SCRIPT" ]]; then
    # 使用 auto 模式，自动识别平台并生成规范路径
    # 错误日志保存到 oss_upload.log
    python3 "$OSS_SCRIPT" auto "$OUTPUT_DIR/screenshots" \
        --video-url "$VIDEO_URL" --metadata "$OUTPUT_DIR/metadata.json" \
        --public --format json > "$OSS_URLS_FILE" 2> "$OSS_LOG_FILE"
    
    EXIT_CODE=$?
    
    if [[ -s "$OSS_URLS_FILE" ]]; then
        URL_COUNT=$(python3 -c "import json; print(len([x for x in json.load(open('$OSS_URLS_FILE')) if x.get('success')]))" 2>/dev/null || echo "0")
        [[ "$URL_COUNT" -gt 0 ]] && echo "✅ OSS 上传成功 | $URL_COUNT 张" || { echo "⚠️  OSS 上传失败"; echo "[]" > "$OSS_URLS_FILE"; }
    else
        echo "⚠️  OSS 上传失败，使用本地路径"
        echo "[]" > "$OSS_URLS_FILE"
    fi
    
    # 上传封面图
    COVER_FILE="$OUTPUT_DIR/cover_url.txt"
    echo "🖼️  上传封面图..." >> "$OSS_LOG_FILE"
    python3 "$OSS_SCRIPT" thumbnail "$OUTPUT_DIR/metadata.json" \
        --public --format json >> "$COVER_FILE" 2>> "$OSS_LOG_FILE"
    
    if [[ -f "$COVER_FILE" ]]; then
        COVER_URL=$(python3 -c "import json; print(json.load(open('$COVER_FILE')).get('oss_url', ''))" 2>/dev/null)
        if [[ -n "$COVER_URL" ]]; then
            echo "✅ 封面上传成功：$COVER_URL" >> "$OSS_LOG_FILE"
            # 更新元数据中的 thumbnail 字段
            python3 << PYEOF >> "$OSS_LOG_FILE" 2>&1
import json
with open('$OUTPUT_DIR/metadata.json', 'r+', encoding='utf-8') as f:
    data = json.load(f)
    data['thumbnail'] = '$COVER_URL'
    f.seek(0)
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.truncate()
print("✅ 元数据已更新")
PYEOF
        else
            echo "⚠️  封面上传失败，使用原始 URL" >> "$OSS_LOG_FILE"
        fi
    fi
else
    echo "⚠️  OSS 脚本不存在，使用本地路径"
    echo "[]" > "$OSS_URLS_FILE"
fi
save_progress "7" "done"
fi

# Step 8: 渲染最终 Markdown（截图和 OSS 完成后）
echo "📝 Step 8: 渲染 Markdown..."
SUMMARY_FILE="$OUTPUT_DIR/summary.md"

# 重新调用 AI 脚本，让它读取已上传的截图 URL 并渲染最终 Markdown
python3 "$AI_SCRIPT" "$SUBTITLE_FILE" "$OUTPUT_DIR/metadata.json" "$SUMMARY_FILE" 2>/dev/null || true

if [[ -f "$SUMMARY_FILE" ]]; then
    echo "✅ Markdown 渲染完成"
    rm -f "$TEMP_SUMMARY" 2>/dev/null
else
    echo "⚠️  Markdown 渲染失败，使用临时文件"
    [[ -f "$TEMP_SUMMARY" ]] && mv "$TEMP_SUMMARY" "$SUMMARY_FILE"
fi

# Step 9: 输出
echo "📁 Step 9: 整理输出..."
save_progress "9" "done"

echo ""
echo "================================"
echo "✅ 处理完成！"
echo "================================"
echo "📁 $OUTPUT_DIR"
echo ""

[[ "$VERBOSE" == "true" ]] && { echo "📄 文件:"; ls -lh "$OUTPUT_DIR"; echo "📸 截图:"; ls "$OUTPUT_DIR/screenshots/"; } || echo "📄 总结：$SUMMARY_FILE | 截图：$(ls "$OUTPUT_DIR/screenshots/" 2>/dev/null | wc -l) 张"

# 清理
[[ "$KEEP_VIDEO" != "true" ]] && { rm -f "$OUTPUT_DIR/video.mp4" "$OUTPUT_DIR/audio.mp3" 2>/dev/null; echo "🧹 已清理视频/音频"; } || echo "💾 保留视频/音频"

# 推送
[[ "$AUTO_PUSH" == "true" && -n "$NOTION_VIDEO_SUMMARY_DATABASE_ID" ]] && { echo ""; echo "📤 推送到 Notion..."; python3 "$SCRIPT_DIR/push-to-notion.py" "$SUMMARY_FILE" "$NOTION_VIDEO_SUMMARY_DATABASE_ID"; } || echo "📤 推送：python3 push-to-notion.py $SUMMARY_FILE"

# 截图状态
[[ $(python3 -c "import json; print(len([x for x in json.load(open('$OSS_URLS_FILE')) if x.get('success')]))" 2>/dev/null || echo 0) -gt 0 ]] && echo "📸 截图：✅ 已上传" || echo "📸 截图：⚠️  本地"
echo ""
