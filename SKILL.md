---
name: video-summarizer
description: "将 B 站/YouTube/小红书/抖音视频转换为结构化 Notion 总结文档，自动上传截图，一键推送 Notion"
metadata:
  {
    "hermes":
      {
        "emoji": "🎬",
        "requires": { "bins": ["ffmpeg (>=6.1)", "yt-dlp (>=2026.03.17)"], "env": ["LLM_API_KEY", "LLM_BASE_URL", "ALIYUN_OSS_AK", "ALIYUN_OSS_SK", "ALIYUN_OSS_BUCKET_ID", "ALIYUN_OSS_ENDPOINT"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "ffmpeg yt-dlp",
              "bins": ["ffmpeg", "yt-dlp"],
              "label": "Install ffmpeg and yt-dlp (brew)",
            },
            {
              "id": "apt",
              "kind": "apt",
              "packages": "ffmpeg yt-dlp",
              "bins": ["ffmpeg", "yt-dlp"],
              "label": "Install ffmpeg and yt-dlp (apt)",
            },
            {
              "id": "choco",
              "kind": "choco",
              "packages": "ffmpeg yt-dlp",
              "bins": ["ffmpeg", "yt-dlp"],
              "label": "Install ffmpeg and yt-dlp (choco - Windows)",
            },
            {
              "id": "pip",
              "kind": "pip",
              "packages": "requests==2.31.0 oss2==2.18.4 python-dotenv==1.0.1 biliup==0.4.86",
              "label": "Install Python dependencies",
            },
          ],
      },
  }
---

# Video Summarizer — Hermes Skill

将 B 站/YouTube/小红书/抖音视频转换为结构化 Notion 总结文档，自动上传截图，一键推送 Notion。

**版本**: 1.1.0  
**发布**: 2026-06-22  
**许可**: MIT  
**作者**: Ajay Hao

> ⚠️ **安全提示**: 本技能会将视频内容发送至第三方 AI 服务进行分析。建议使用专用 API Key，OSS Bucket 配置最小权限。详见 [安全说明](references/security.md)。

---

## 📖 核心能力

- 🎬 **多平台支持**: B 站、YouTube、小红书、抖音
- 📝 **智能分析**: AI 提取关键概念、核心要点、注意事项
- 📸 **截图嵌入**: 基于 AI 分析结果自动生成关键帧截图
- ☁️ **图床集成**: 阿里云 OSS 自动上传，永久链接
- 🚀 **双通道推送**: Obsidian 本地（默认）+ Notion 云端（--notion 开启）

### 技术特性

- **双模式转录**: Plan A（官方字幕）优先，Plan B（语音转录）兜底
- **并行优化**: 字幕下载与视频下载并行执行，节省 ~32% 时间
- **GPU 自适应**: 自动检测显存，选择最优 Whisper 模型
- **断点续跑**: 支持从中断点恢复，避免重复处理
- **四层标签**: 标题 hashtag → 元数据 → AI 关键词 → 默认值

---

## 🎯 快速开始

```bash
# 1. 安装依赖
pip3 install requests oss2 python-dotenv
# 系统依赖: ffmpeg (>=6.1), yt-dlp (>=2026.03.17)

# 2. 配置环境变量 ($AGENT_HOME/.env)
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-v4-pro
ALIYUN_OSS_AK=your_ak
ALIYUN_OSS_SK=your_sk
ALIYUN_OSS_BUCKET_ID=your_bucket
ALIYUN_OSS_ENDPOINT=oss-cn-shanghai.aliyuncs.com

# 3. 运行
cd scripts
./video-summarize.sh "https://www.bilibili.com/video/BV1xxxx"

# 4. 查看结果
cat $TMPDIR/video-summarizer-*/summary.md  # Linux: /tmp/...  Windows: %TEMP%/...
```

---

## ⚙️ 环境变量

### 必需配置

| 变量 | 说明 | 示例 |
|------|------|------|
| `LLM_API_KEY` | AI 分析 API Key | `sk-xxx` |
| `LLM_BASE_URL` | LLM API 地址（OpenAI 兼容） | `https://api.deepseek.com` |
| `LLM_MODEL` | 模型名称 | `deepseek-v4-pro` |
| `ALIYUN_OSS_AK` | 阿里云 OSS AccessKey |  |
| `ALIYUN_OSS_SK` | 阿里云 OSS Secret |  |
| `ALIYUN_OSS_BUCKET_ID` | OSS Bucket 名称 |  |
| `ALIYUN_OSS_ENDPOINT` | OSS 区域端点 | `oss-cn-shanghai.aliyuncs.com` |

### 可选配置

| 变量 | 说明 | 默认行为 |
|------|------|----------|
| `OBSIDIAN_VAULT_PATH` | Obsidian Vault 路径（推荐配置） | 未配置时跳过存储 |
| `GROQ_API_KEY` | Groq 语音转录加速 | 未配置时使用本地 Faster-Whisper |
| `NOTION_API_KEY` | Notion API Key | 未配置时跳过推送 |
| `NOTION_VIDEO_SUMMARY_DATABASE_ID` | Notion 数据库 ID | 同上 |
| `WHISPER_MODEL` | 本地 Whisper 模型 | `base` |

通过 `LLM_BASE_URL` 可接入 DeepSeek / DashScope / OpenAI / Groq 等任意 OpenAI 兼容平台。

---

## 🏗️ 处理流程

```
用户输入 (视频 URL)
       ↓
Step 1: 平台识别 + 元数据
       ↓
┌──────┴──────┐
↓             ↓
Step 2: 字幕   Step 3: 视频下载  ← 并行执行
       ↓             ↓
       └──────┬──────┘
              ↓
Step 4: 文本提取 (VTT → TXT / Plan B 转录)
       ↓
Step 5: AI 分析 (OpenAI 兼容接口)
       ↓
Step 6: 截图生成 (ffmpeg, 基于 AI 时间戳)
       ↓
Step 7: OSS 上传 (截图 + 封面)
       ↓
Step 8: Markdown 渲染
       ↓
Step 9: Notion 推送 (可选, --notion)
       ↓
Step 10: Obsidian 本地存储 (默认, --no-obsidian 禁用)
```

### 技术栈

| 层级 | 技术 |
|------|------|
| 编排层 | Bash (`video-summarize.sh`) |
| 分析层 | Python + OpenAI 兼容 LLM API |
| 转录层 | Groq API (可选) / Faster-Whisper (本地) |
| 工具层 | yt-dlp, ffmpeg, oss2, requests |

---

## 📋 脚本清单

| 脚本 | 功能 |
|------|------|
| `video-summarize.sh` | 主流程编排（Plan A/B 自动选择） |
| `analyze-subtitles-ai.py` | AI 分析 + Markdown 渲染 |
| `upload-to-oss.py` | OSS 图床上传（截图 + 封面） |
| `push-to-obsidian.py` | Obsidian Vault 写入（默认） |
| `push-to-notion.py` | Notion 推送（--notion 触发） |
| `transcribe-audio.py` | 语音转录（GPU 自适应） |
| `llm_client.py` | 多平台 LLM 客户端（OpenAI 兼容） |
| `bili-login.sh` | B 站扫码登录 |
| `douyin_downloader.py` | 抖音专用下载器 |
| `check-config.sh` | 配置检查 |

---

## 📁 输出结构

```
output/
├── summary.md              # 📝 最终总结（主要成果）
├── ai_result.json          # 🧠 AI 分析原始结果
├── screenshot_urls.txt     # 🔗 截图 OSS 链接
├── metadata.json           # 📊 视频元数据
├── transcript.txt          # 📄 纯文本字幕
├── audio.txt               # 🎤 语音转录原始文本（Plan B）
├── cover_url.txt           # ☁️ 封面 OSS 上传结果
├── screenshot_times.txt    # ⏱️ 截图时间戳记录
├── screenshots/            # 📸 截图原图
├── cover.jpg              # 🖼️ 封面图
└── *.log                   # 📋 日志文件
```

---

## 🏷️ 标签策略（四层提取）

1. **标题 hashtag** → `#标签` 格式提取
2. **元数据 tags** → yt-dlp 原始标签
3. **AI 关键词** → AI 分析的核心概念
4. **默认值** → 视频总结 / AI 分析 / 教程 / 技巧 / 知识分享

规则：2-15 字符，最多 5 个，自动去重，优先级 1→2→3→4。

---

## 📝 输出格式

生成的 `summary.md` 包含：
1. 标题 + Tags + Author
2. 📝 Note — AI 概述（150-250 字）
3. 📺 视频信息 — 链接/时长/播放数据
4. 📚 关键概念 — 术语表格（3-5 个）
5. 🎯 核心要点 — emoji + 描述 + 时间戳（5-8 个）
6. 🎬 视频章节 — 标题 + 时间轴 + 截图
7. ⚠️ 注意事项 — 特别提醒（2-4 个）
8. 💡 总结 — AI 归纳（200-300 字）

---

## 📊 性能基准（10 分钟视频）

| 平台 | Plan A | Plan B（本地） | Plan B（Groq） |
|------|--------|----------------|----------------|
| Bilibili | ~90 秒 | ~150 秒 | ~120 秒 |
| YouTube | ~90 秒 | ~150 秒 | ~120 秒 |
| 小红书 | - | ~150 秒 | ~120 秒 |
| 抖音 | - | ~150 秒 | ~120 秒 |

---

## 📓 Obsidian 本地存储

### 设计理念

四种场景，一条命令覆盖：

| 你的配置 | 命令 | 效果 |
|----------|------|------|
| 都不配 | `--no-obsidian` | 仅抓取，会话中输出 Markdown |
| 仅 Notion | `--no-obsidian --notion` | 推送到 Notion |
| **仅 Obsidian**（推荐） | （零参数） | 推送到 Obsidian，零外部依赖 |
| 两者都配 | `--notion` | Obsidian + Notion 双存档 |

> 💡 无论哪种配置，`summary.md` 始终在临时目录生成，可随时手动查阅。

### 功能

视频总结完成后，**默认推送到 Obsidian**——本地优先，零外部依赖。

### 存储结构

```
{Obsidian Vault}/
└── 1-输入-收件箱/
    └── 视频总结/
        ├── bilibili_BV1xxx_20260622.md      # YAML frontmatter + status: inbox
        └── attachments/
            ├── screenshot_01.jpg
            └── cover.jpg
```

### 配置

```bash
# 在 $AGENT_HOME/.env 中添加
# macOS
OBSIDIAN_VAULT_PATH=/Users/name/ObsidianVault
# Windows
OBSIDIAN_VAULT_PATH=D:\ObsidianVault
# Linux
OBSIDIAN_VAULT_PATH=/home/name/ObsidianVault
```

### 使用

```bash
# 默认：推送到 Obsidian
./video-summarize.sh "https://www.bilibili.com/video/BV1xxxx"

# Obsidian + Notion 两者
./video-summarize.sh "https://www.bilibili.com/video/BV1xxxx" --notion

# 仅 Notion
./video-summarize.sh "https://www.bilibili.com/video/BV1xxxx" --notion --no-obsidian

# 仅分析不推送
./video-summarize.sh "https://www.bilibili.com/video/BV1xxxx" --no-obsidian
```

---

## 🔜 后续优化

- [ ] 单元测试（核心函数覆盖率 80%+）
- [ ] 性能优化（截图并行上传、结果缓存）
- [ ] 支持更多平台（TikTok、Instagram Reels）

---

## 📞 更多文档

- **平台详情**: [references/platforms.md](references/platforms.md) — 四平台支持、Plan A/B 对比
- **安全说明**: [references/security.md](references/security.md) — 隐私、端点、权限建议
- **故障排查**: [references/troubleshooting.md](references/troubleshooting.md) — 常见问题解决
- **快速入门**: [README.md](README.md) — 5 分钟上手
- **变更历史**: [CHANGELOG.md](CHANGELOG.md) — 版本演进
- **提示词配置**: [prompt.json](prompt.json) — AI 分析参数

---

**维护人**: Ajay Hao  
**项目地址**: https://github.com/AjayHao/video-summarizer  
**Hermes Skill**: 适用于 Hermes Agent 平台
