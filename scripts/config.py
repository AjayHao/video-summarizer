"""
config.py - video-summarizer 统一配置（Python 端）
所有脚本 import config 即可获取环境变量和路径。

加载链：$AGENT_HOME/.env → $HERMES_HOME/.env → ~/.hermes/.env → ~/.openclaw/.env
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def _init():
    """初始化 AGENT_HOME 并加载 .env。模块 import 时自动执行。"""
    # 1. 确认 AGENT_HOME
    agent_home = os.getenv('AGENT_HOME') or os.getenv('HERMES_HOME')
    if not agent_home:
        for d in [Path.home() / '.hermes', Path.home() / '.openclaw']:
            if d.exists():
                agent_home = str(d)
                break
    if agent_home:
        os.environ['AGENT_HOME'] = agent_home
    else:
        agent_home = str(Path.home() / '.hermes')
        os.environ['AGENT_HOME'] = agent_home

    # 2. 加载 .env
    env_path = Path(agent_home) / '.env'
    if env_path.exists():
        load_dotenv(env_path)


# 模块导入时自动初始化
_init()

# ====== 导出环境变量 ======
AGENT_HOME = os.environ['AGENT_HOME']

# OSS
OSS_AK = os.getenv('ALIYUN_OSS_AK', '')
OSS_SK = os.getenv('ALIYUN_OSS_SK', '')
OSS_BUCKET = os.getenv('ALIYUN_OSS_BUCKET_ID', '')
OSS_ENDPOINT = os.getenv('ALIYUN_OSS_ENDPOINT', '')

# LLM
LLM_API_KEY = os.getenv('LLM_API_KEY', '')
LLM_BASE_URL = os.getenv('LLM_BASE_URL', '')
LLM_MODEL = os.getenv('LLM_MODEL', '')

# Obsidian
OBSIDIAN_VAULT_PATH = os.getenv('OBSIDIAN_VAULT_PATH', '')

# Notion
NOTION_API_KEY = os.getenv('NOTION_API_KEY', '')
NOTION_DATABASE_ID = os.getenv('NOTION_VIDEO_SUMMARY_DATABASE_ID', '')

# Groq
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
