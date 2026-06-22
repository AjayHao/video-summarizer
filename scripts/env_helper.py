"""
env_helper.py - $AGENT_HOME 归一入口
所有脚本统一 import 此模块，不再需要自行处理路径降级。

用法：
    import env_helper  # 自动初始化 AGENT_HOME 并加载 .env
    # 后续直接用 os.environ 读变量即可
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def _init():
    """确保 $AGENT_HOME 已设置并加载 .env。模块 import 时自动执行。"""
    if os.getenv('AGENT_HOME'):
        _load()
        return

    # 推断 Agent 目录
    candidates = []
    hermes = os.getenv('HERMES_HOME')
    if hermes:
        candidates.append(Path(hermes))
    candidates.extend([
        Path.home() / '.hermes',
        Path.home() / '.openclaw',
    ])

    for d in candidates:
        if d.exists():
            os.environ['AGENT_HOME'] = str(d)
            break
    else:
        os.environ['AGENT_HOME'] = str(Path.home() / '.hermes')

    _load()


def _load():
    env_path = Path(os.environ['AGENT_HOME']) / '.env'
    if env_path.exists():
        load_dotenv(env_path)


_init()
