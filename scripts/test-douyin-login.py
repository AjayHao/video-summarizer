#!/usr/bin/env python3
"""
快速测试抖音自动登录脚本
用法：python3 test-douyin-login.py
"""

import sys
from pathlib import Path

# 检查依赖
try:
    from playwright.sync_api import sync_playwright
    print("✅ Playwright 已安装")
except ImportError:
    print("❌ Playwright 未安装")
    print("\n安装命令：")
    print("  pip3 install playwright --break-system-packages")
    print("  playwright install chromium")
    sys.exit(1)

# 检查 Chromium
chromium_path = Path.home() / ".cache/ms-playwright/chromium_headless_shell-1208"
if chromium_path.exists():
    print(f"✅ Chromium 已安装：{chromium_path}")
else:
    print("❌ Chromium 未安装")
    print("\n安装命令：")
    print("  playwright install chromium")
    sys.exit(1)

print("\n✅ 环境检查通过！\n")
print("运行自动登录：")
print("  python3 douyin-login-auto.py")
