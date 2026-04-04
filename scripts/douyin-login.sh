#!/bin/bash
# douyin-login.sh - 获取抖音 Cookies
# 用法：./douyin-login.sh

COOKIES_DIR="$HOME/.cookies"
COOKIES_FILE="$COOKIES_DIR/douyin_cookies.txt"

mkdir -p "$COOKIES_DIR"

echo "🍪 抖音 Cookies 获取工具"
echo ""
echo "由于抖音需要登录才能下载视频，请按照以下步骤获取 Cookies："
echo ""
echo "1️⃣  打开浏览器（推荐 Chrome/Edge）"
echo "2️⃣  访问抖音：https://www.douyin.com"
echo "3️⃣  登录你的抖音账号（扫码或手机号）"
echo "4️⃣  按 F12 打开开发者工具"
echo "5️⃣  切换到 Network（网络）标签"
echo "6️⃣  刷新页面"
echo "7️⃣  找到任意一个请求（如 www.douyin.com）"
echo "8️⃣  复制请求头中的 Cookie 值"
echo ""
echo "或者使用浏览器扩展："
echo "  - Chrome: 'Get cookies.txt LOCALLY'"
echo "  - Edge: 'cookies.txt'"
echo ""

# 检查是否有浏览器
if command -v google-chrome &> /dev/null; then
    echo "🌐 检测到 Chrome，尝试自动获取..."
    echo ""
    echo "请安装以下扩展之一："
    echo "  - Get cookies.txt LOCALLY: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc"
    echo ""
    echo "安装后访问抖音，导出 cookies.txt 并保存到：$COOKIES_FILE"
    echo ""
elif command -v firefox &> /dev/null; then
    echo "🌐 检测到 Firefox，尝试自动获取..."
    echo ""
    echo "请安装以下扩展："
    echo "  - cookies.txt: https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/"
    echo ""
    echo "安装后访问抖音，导出 cookies.txt 并保存到：$COOKIES_FILE"
    echo ""
fi

echo "📝 手动输入 Cookies（可选）"
echo ""
echo "如果你已经复制了 Cookie，请粘贴到下方（以 __tea_cache_tokens_ 开头）："
echo "（按 Ctrl+C 跳过）"
echo ""

read -p "粘贴 Cookies: " -r COOKIE_INPUT

if [[ -n "$COOKIE_INPUT" ]]; then
    # 保存 Cookies
    echo "# Netscape HTTP Cookie File" > "$COOKIES_FILE"
    echo "# 抖音 Cookies - 获取于 $(date)" >> "$COOKIES_FILE"
    echo "" >> "$COOKIES_FILE"
    
    # 解析 Cookie 并保存为 Netscape 格式
    # 简单处理：直接保存原始 Cookie
    echo "www.douyin.com	TRUE	/	TRUE	0	__tea_cache_tokens_	${COOKIE_INPUT}" >> "$COOKIES_FILE"
    
    echo ""
    echo "✅ Cookies 已保存到：$COOKIES_FILE"
    echo ""
    echo "⚠️  注意：Cookies 有效期约 30-90 天，过期后请重新获取"
else
    echo ""
    echo "⏭️  跳过手动输入"
fi

echo ""
echo "📋 验证 Cookies："
if [[ -f "$COOKIES_FILE" ]]; then
    echo "   ✅ Cookies 文件已创建：$COOKIES_FILE"
    echo "   📄 查看内容：cat $COOKIES_FILE"
    echo ""
    echo "🎬 测试下载："
    echo "   ~/.openclaw/skills/video-summarizer/scripts/video-summarize.sh \\"
    echo "       'https://v.douyin.com/xxx' \\"
    echo "       --cookies $COOKIES_FILE"
else
    echo "   ⚠️  Cookies 文件未创建"
fi

echo ""
