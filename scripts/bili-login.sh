#!/bin/bash
# bili-login.sh - B 站扫码登录获取 Cookies
# 用法：./bili-login.sh [输出文件]

set -e

COOKIE_FILE="${1:-$HOME/.cookies/bilibili_cookies.txt}"
BILIUP_COOKIE="$HOME/.config/biliup/cookies.json"

echo "================================"
echo "📱 B 站扫码登录"
echo "================================"
echo ""

# 检查 biliup 是否安装
if ! command -v biliup &>/dev/null; then
    echo "❌ biliup 未安装"
    echo ""
    echo "安装命令:"
    echo "  pip3 install biliup --break-system-packages"
    exit 1
fi

# 创建目录
mkdir -p "$(dirname "$COOKIE_FILE")"
mkdir -p "$(dirname "$BILIUP_COOKIE")"

# 执行扫码登录
echo "请使用 B 站 APP 扫码："
echo ""
biliup login

# 检查登录是否成功
if [[ ! -f "$BILIUP_COOKIE" ]]; then
    echo ""
    echo "❌ 登录失败，未找到 cookies.json"
    exit 1
fi

echo ""
echo "✅ 登录成功"
echo ""

# 转换格式
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "🔄 转换 Cookies 格式..."
python3 "$SCRIPT_DIR/convert-bili-cookie.py" "$BILIUP_COOKIE" "$COOKIE_FILE"

if [[ $? -eq 0 && -f "$COOKIE_FILE" ]]; then
    echo "✅ Cookies 已保存：$COOKIE_FILE"
    echo ""
    echo "📄 Cookie 内容预览:"
    head -5 "$COOKIE_FILE"
    echo "..."
    echo ""
    echo "📊 统计:"
    wc -l "$COOKIE_FILE" | awk '{print "   共 " $1 " 行"}'
else
    echo "❌ 格式转换失败"
    exit 1
fi

echo ""
echo "================================"
echo "✅ 登录完成"
echo "================================"
