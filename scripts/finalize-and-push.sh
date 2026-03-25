#!/bin/bash
# finalize-and-push.sh - Plan A 最后一步：推送总结到聊天框 + Notion
# 用法：./finalize-and-push.sh <输出目录>

set -e

OUTPUT_DIR="$1"

if [[ -z "$OUTPUT_DIR" || ! -d "$OUTPUT_DIR" ]]; then
    echo "❌ 错误：请指定有效的输出目录"
    echo "用法：./finalize-and-push.sh <输出目录>"
    exit 1
fi

SUMMARY_FILE="$OUTPUT_DIR/summary-ai.md"
if [[ ! -f "$SUMMARY_FILE" ]]; then
    SUMMARY_FILE="$OUTPUT_DIR/summary.md"
fi

if [[ ! -f "$SUMMARY_FILE" ]]; then
    echo "❌ 错误：找不到总结文件"
    exit 1
fi

echo "========================================"
echo "📤 Plan A 最后一步：推送总结"
echo "========================================"
echo ""

# ==================== Step 1: 在聊天框推送总结 ====================
echo "📱 Step 1/2: 在聊天框推送总结预览..."

# 提取关键信息
TITLE=$(grep "^# " "$SUMMARY_FILE" | sed 's/^# //')
NOTE=$(sed -n '/## 📝 Note/,/---/p' "$SUMMARY_FILE" | grep -v "## 📝 Note" | grep -v "^---$" | head -5)
TAGS=$(grep "\*\*Tags:\*\*" "$SUMMARY_FILE" | sed 's/.*Tags:\*\* //')
AUTHOR=$(grep "\*\*Author:\*\*" "$SUMMARY_FILE" | sed 's/.*Author:\*\* //')
VIDEO_URL=$(grep "\*\*链接:\*\*" "$SUMMARY_FILE" | sed 's/.*链接:\*\* //')

# 生成推送消息
cat << EOF

━━━━━━━━━━━━━━━━━━━━━━━━
🎬 视频总结已完成！

📝 **$TITLE**

$TAGS
👤 UP 主：$AUTHOR
🔗 $VIDEO_URL

━━━━━━━━━━━━━━━━━━━━━━━━

📝 **概述**
$NOTE

━━━━━━━━━━━━━━━━━━━━━━━━

✅ 处理完成！

请老大审阅：
1. 查看完整总结：$SUMMARY_FILE
2. 确认无误后回复"推送到 Notion"
3. 或提出修改意见

EOF

echo ""
echo "✅ 总结预览已生成（见上方）"
echo ""

# ==================== Step 2: 等待用户确认 ====================
echo "⏳ Step 2/2: 等待老大确认..."
echo ""
echo "请老大回复以下指令之一："
echo "  - '推送到 Notion' 或 'ok' → 推送到 Notion"
echo "  - '修改 XXX' → 根据意见修改"
echo "  - '取消' → 放弃推送"
echo ""
echo "（脚本暂停，等待用户输入...）"
echo ""

# 注意：实际使用中，这部分由用户手动回复
# 脚本只负责生成预览和推送

# ==================== Step 3: 推送到 Notion（如果确认） ====================
# 这部分需要用户明确确认后执行

echo "========================================"
echo "📋 下一步操作"
echo "========================================"
echo ""
echo "1. 老大审阅上方的总结预览"
echo "2. 回复确认指令后，执行："
echo ""
echo "   python3 ~/.openclaw/skills/video-summarizer/scripts/push-to-notion.py \\"
echo "       $SUMMARY_FILE \\"
echo "       [Notion Database ID]"
echo ""
echo "3. 或手动查看完整总结："
echo "   cat $SUMMARY_FILE"
echo ""

# 如果有 Notion Database ID，自动推送
NOTION_DB_ID="${NOTION_VIDEO_SUMMARY_DATABASE_ID:-}"

if [[ -n "$NOTION_DB_ID" && "$AUTO_PUSH_TO_NOTION" == "true" ]]; then
    echo "📤 自动推送到 Notion..."
    python3 ~/.openclaw/skills/video-summarizer/scripts/push-to-notion.py "$SUMMARY_FILE" "$NOTION_DB_ID"
else
    echo "⏸️  等待老大确认后再推送到 Notion"
fi

echo ""
