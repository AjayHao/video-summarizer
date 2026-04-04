#!/bin/bash
# douyin-login-v2.sh - 抖音 Cookies 获取工具（多方案）
# 用法：./douyin-login-v2.sh [方案]
# 方案：auto | browser | manual

set -e

COOKIES_DIR="$HOME/.cookies"
COOKIES_FILE="$COOKIES_DIR/douyin_cookies.txt"
BROWSER="${1:-auto}"  # auto, chrome, firefox, edge, manual

mkdir -p "$COOKIES_DIR"

echo "================================"
echo "🍪 抖音 Cookies 获取工具"
echo "================================"
echo ""

# 方案 1：从浏览器自动读取（推荐）
get_cookies_from_browser() {
    local browser="$1"
    echo "🔍 尝试从 $browser 读取 Cookies..."
    
    # 使用 yt-dlp 从浏览器读取并保存
    if yt-dlp --cookies-from-browser "$browser" \
              --cookies "$COOKIES_FILE" \
              --simulate \
              "https://www.douyin.com" 2>/dev/null; then
        echo "✅ 从 $browser 读取 Cookies 成功"
        return 0
    else
        echo "❌ 从 $browser 读取失败"
        return 1
    fi
}

# 方案 2：手动导出
cookies_manual() {
    echo "📝 手动导出方案"
    echo ""
    echo "请按以下步骤操作："
    echo ""
    echo "1️⃣  打开浏览器访问 https://www.douyin.com"
    echo "2️⃣  登录你的抖音账号"
    echo "3️⃣  按 F12 打开开发者工具"
    echo "4️⃣  切换到 Application/应用 标签"
    echo "5️⃣  左侧选择 Cookies → https://www.douyin.com"
    echo "6️⃣  复制所有 Cookies 或使用扩展导出"
    echo ""
    echo "推荐扩展："
    echo "  Chrome: Get cookies.txt LOCALLY"
    echo "  Edge: cookies.txt"
    echo ""
    echo "7️⃣  保存到：$COOKIES_FILE"
    echo ""
    
    read -p "按回车键打开浏览器..."
    
    # 尝试打开默认浏览器
    if command -v xdg-open &>/dev/null; then
        xdg-open "https://www.douyin.com" &
    elif command -v open &>/dev/null; then
        open "https://www.douyin.com" &
    fi
}

# 主逻辑
case "$BROWSER" in
    auto)
        echo "🤖 自动模式：尝试从浏览器读取"
        echo ""
        
        # 尝试支持的浏览器
        for browser in chrome chromium edge firefox brave; do
            if get_cookies_from_browser "$browser"; then
                echo ""
                echo "✅ Cookies 获取成功！"
                echo "📁 保存位置：$COOKIES_FILE"
                exit 0
            fi
        done
        
        echo ""
        echo "⚠️  自动读取失败，请尝试手动模式："
        echo "   ./douyin-login-v2.sh manual"
        exit 1
        ;;
        
    chrome|chromium|edge|firefox|brave|safari)
        if get_cookies_from_browser "$BROWSER"; then
            echo ""
            echo "✅ Cookies 获取成功！"
            echo "📁 保存位置：$COOKIES_FILE"
        else
            echo ""
            echo "❌ 从 $BROWSER 获取失败"
            echo ""
            echo "请确保："
            echo "  1. $BROWSER 已安装"
            echo "  2. 已在 $BROWSER 中登录抖音"
            exit 1
        fi
        ;;
        
    manual)
        cookies_manual
        ;;
        
    *)
        echo "用法：$0 [方案]"
        echo ""
        echo "方案："
        echo "  auto     - 自动尝试所有浏览器（默认）"
        echo "  chrome   - 从 Chrome 读取"
        echo "  firefox  - 从 Firefox 读取"
        echo "  edge     - 从 Edge 读取"
        echo "  manual   - 手动导出"
        echo ""
        echo "示例："
        echo "  $0 auto      # 自动尝试"
        echo "  $0 chrome    # 指定 Chrome"
        echo "  $0 manual    # 手动导出"
        exit 1
        ;;
esac

# 验证结果
if [[ -f "$COOKIES_FILE" ]]; then
    echo ""
    echo "📊 Cookies 文件信息："
    ls -lh "$COOKIES_FILE"
    echo ""
    echo "🧪 测试 Cookies："
    if yt-dlp --cookies "$COOKIES_FILE" --simulate "https://www.douyin.com" 2>/dev/null | head -1; then
        echo "✅ Cookies 有效！"
    else
        echo "⚠️  Cookies 可能无效，请检查"
    fi
    echo ""
    echo "================================"
    echo "✅ 完成"
    echo "================================"
else
    echo ""
    echo "❌ Cookies 文件未创建"
    exit 1
fi
