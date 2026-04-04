#!/bin/bash
# douyin-quickstart.sh - 抖音支持快速开始
# 用法：./douyin-quickstart.sh

set -e

echo "================================"
echo "🎬 抖音支持快速开始"
echo "================================"
echo ""

# 检查 yt-dlp
if ! command -v yt-dlp &>/dev/null; then
    echo "❌ yt-dlp 未安装"
    echo ""
    echo "安装命令："
    echo "  pip3 install yt-dlp --break-system-packages"
    exit 1
fi

echo "✅ yt-dlp 已安装：$(yt-dlp --version)"
echo ""

# 检查浏览器
BROWSER_FOUND=""
for browser in chrome chromium firefox edge brave; do
    if command -v $browser &>/dev/null; then
        BROWSER_FOUND="$browser"
        echo "✅ 检测到浏览器：$browser"
        break
    fi
done

if [[ -z "$BROWSER_FOUND" ]]; then
    echo "⚠️  未检测到支持的浏览器"
    echo ""
    echo "请安装以下浏览器之一："
    echo "  - Google Chrome"
    echo "  - Chromium"
    echo "  - Firefox"
    echo "  - Microsoft Edge"
    echo ""
    echo "然后运行："
    echo "  ./douyin-quickstart.sh"
    exit 1
fi

echo ""
echo "================================"
echo "📱 第一步：登录抖音网页版"
echo "================================"
echo ""
echo "请按以下步骤操作："
echo ""
echo "1️⃣  打开浏览器"
echo "2️⃣  访问 https://www.douyin.com"
echo "3️⃣  使用抖音 APP 扫码登录"
echo "4️⃣  确认登录成功（能看到用户头像）"
echo ""

read -p "按回车键打开浏览器..."

# 打开浏览器
if command -v xdg-open &>/dev/null; then
    xdg-open "https://www.douyin.com" &
elif command -v open &>/dev/null; then
    open "https://www.douyin.com" &
fi

echo ""
echo "请在浏览器中完成登录..."
echo ""
read -p "登录完成后按回车键继续..."

echo ""
echo "================================"
echo "🍪 第二步：获取 Cookies"
echo "================================"
echo ""

# 获取 Cookies
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/douyin-login-v2.sh" "$BROWSER_FOUND"

if [[ $? -eq 0 && -f "$HOME/.cookies/douyin_cookies.txt" ]]; then
    echo ""
    echo "================================"
    echo "✅ 完成！"
    echo "================================"
    echo ""
    echo "📁 Cookies 已保存：$HOME/.cookies/douyin_cookies.txt"
    echo ""
    echo "现在可以处理抖音视频了："
    echo ""
    echo "  $SCRIPT_DIR/video-summarize.sh \\"
    echo "      'https://v.douyin.com/xxx'"
    echo ""
    echo "📚 详细文档：docs/douyin-login-guide.md"
    echo ""
else
    echo ""
    echo "❌ Cookies 获取失败"
    echo ""
    echo "请尝试手动模式："
    echo "  $SCRIPT_DIR/douyin-login-v2.sh manual"
    echo ""
    exit 1
fi
