#!/bin/bash
# config.sh - video-summarizer 统一配置（Shell 端）
# 所有脚本 source 此文件即可获取 AGENT_HOME / PYTHON / TMPDIR / _ah
#
# 用法：source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

# ====== $AGENT_HOME 归一入口 ======
if [ -z "$AGENT_HOME" ]; then
    if [ -n "$HERMES_HOME" ]; then
        export AGENT_HOME="$HERMES_HOME"
    elif [ -d "$HOME/.hermes" ]; then
        export AGENT_HOME="$HOME/.hermes"
    elif [ -d "$HOME/.openclaw" ]; then
        export AGENT_HOME="$HOME/.openclaw"
    else
        export AGENT_HOME="$HOME/.hermes"
    fi
fi

# ====== Python 解释器 ======
# Ubuntu 默认 python3，Windows Hermes 通过 PYTHON=python 覆盖
PYTHON="${PYTHON:-python3}"

# ====== 跨平台临时目录 ======
case "$(uname -s 2>/dev/null)" in
    MINGW*|MSYS*)
        TMPDIR=$(cygpath -w "${TEMP:-/tmp}" 2>/dev/null | sed 's|\\|/|g')
        ;;
    *)
        TMPDIR="/tmp"
        ;;
esac

# ====== 路径辅助函数 ======
# _ah: AGENT_HOME → MSYS 兼容路径（仅 Windows 转换反斜杠）
_ah() {
    case "$(uname -s 2>/dev/null)" in
        MINGW*|MSYS*) echo "$AGENT_HOME" | sed 's|\\|/|g' | sed 's|^\([A-Za-z]\):|/\1|' ;;
        *) echo "$AGENT_HOME" ;;
    esac
}

# ====== 常用路径 ======
ENV_FILE="$(_ah)/.env"
COOKIES_DIR="$HOME/.cookies"
BILI_COOKIES_FILE="$COOKIES_DIR/bilibili_cookies.txt"
