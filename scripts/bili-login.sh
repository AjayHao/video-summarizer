#!/bin/bash
# bili-login.sh - B 站扫码登录获取 Cookies
# 用法：./bili-login.sh [输出文件]

set -e

COOKIE_FILE="${1:-$HOME/.cookies/bilibili_cookies.txt}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# biliup login 默认在当前工作目录保存 cookies.json
BILIUP_COOKIE="$SCRIPT_DIR/cookies.json"

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

# 进入脚本目录执行，确保 cookies.json 保存在正确位置
cd "$SCRIPT_DIR"

# 执行扫码登录
echo "请使用 B 站 APP 扫码："
echo ""
biliup login

# 检查登录是否成功
if [[ ! -f "$BILIUP_COOKIE" ]]; then
    echo ""
    echo "❌ 登录失败，未找到 cookies.json"
    echo "   预期路径：$BILIUP_COOKIE"
    exit 1
fi

echo ""
echo "✅ 登录成功"
echo ""

# 转换格式
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
