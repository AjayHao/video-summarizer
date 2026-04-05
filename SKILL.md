# Video Summarizer — 视频总结生成技能

将 B 站/YouTube/小红书/抖音视频转换为结构化 Notion 总结文档，自动上传截图，一键推送 Notion。

**版本:** v0.1.5  
**发布日期:** 2026-04-05  
**状态:** ✅ 并行优化 · 标签提取 · OSS 路径修复 · GPU 自适应 · 日志完善

---

## 平台支持状态

| 平台 | 支持状态 | 字幕支持 | Plan B 语音转录 | 说明 |
|------|----------|----------|----------------|------|
| **Bilibili** | ✅ 完整支持 | ✅ 官方 + 自动 | ✅ 支持 | 推荐扫码登录获取 Cookies |
| **YouTube** | ✅ 完整支持 | ✅ 自动字幕 | ✅ 支持 | 需网络可达 |
| **小红书** | ✅ 基本支持 | ❌ 无字幕 | ✅ 支持 | 依赖 Plan B 语音转录 |
| **抖音** | ✅ 完整支持 | ❌ 无字幕 | ✅ 支持 | 专用下载工具（无需 Cookies） |

---

## 🏗️ 系统架构

### 数据流图

```
用户输入 (视频 URL)
       ↓
Step 1: 平台识别 + 元数据 (yt-dlp / douyin_downloader.py)
       ↓
┌──────┴──────┐
↓             ↓
Step 2: 字幕   Step 3: 视频下载  ← 并行执行
       ↓             ↓
       └──────┬──────┘
              ↓
Step 4: 文本提取 (VTT → TXT / Plan B 转录)
       ↓
Step 5: AI 分析 (DashScope API - qwen3.5-plus)
       ↓
Step 6: 截图生成 (ffmpeg, 基于 AI 时间戳)
       ↓
Step 7: OSS 上传 (upload-to-oss.py)
       ↓
Step 8: Markdown 渲染 (analyze-subtitles-ai.py)
       ↓
Step 9: Notion 推送 (push-to-notion.py, 可选)
```

### 技术栈

| 层级 | 技术 |
|------|------|
| 编排层 | Bash (video-summarize.sh) |
| 分析层 | Python + DashScope API (qwen3.5-plus) |
| 转录层 | Faster-Whisper (本地) / Groq API / 硅基流动 |
| 工具层 | yt-dlp, ffmpeg, oss2, requests |

### 模块依赖关系

```
video-summarize.sh (主编排)
│
├── yt-dlp (元数据获取、视频下载、字幕下载)
│
├── douyin_downloader.py (抖音专用)
│   └── requests
│
├── download-audio.sh (Plan B)
│   └── yt-dlp
│
├── transcribe-audio.py (Plan B)
│   ├── Faster-Whisper (本地 GPU/CPU)
│   ├── Groq API (whisper-large-v3)
│   └── 硅基流动 (FunAudioLLM/SenseVoiceSmall)
│
├── analyze-subtitles-ai.py (AI 分析 + Markdown 渲染)
│   ├── requests (DashScope API)
│   ├── prompt.json (AI 提示词配置)
│   └── templates/summary.md (模板)
│
├── upload-to-oss.py (OSS 上传)
│   ├── oss2 (阿里云 OSS SDK)
│   └── requests (封面下载)
│
└── push-to-notion.py (Notion 推送)
    └── requests (Notion API)
```

### 数据文件依赖

| 文件 | 来源 | 字段 | 被依赖 |
|------|------|------|--------|
| `metadata.json` | yt-dlp / douyin_downloader | title, uploader, duration, thumbnail | analyze, upload, push |
| `transcript.txt` | VTT 提取 / Plan B 转录 | 纯文本字幕 | analyze |
| `ai_result.json` | analyze-subtitles-ai.py | note, key_points, concepts, warnings | 截图提取，Markdown 渲染 |
| `screenshot_urls.txt` | upload-to-oss.py | [{local_path, oss_url, success}] | Markdown 渲染 |
| `.progress.json` | video-summarize.sh | current_step, status, timestamp | 断点续跑检测 |

---

## 🚀 快速开始

### 1. 扫码登录（首次使用）

```bash
~/.openclaw/skills/video-summarizer/scripts/bili-login.sh
```

### 2. 处理视频

```bash
~/.openclaw/skills/video-summarizer/scripts/video-summarize.sh "视频 URL"
```

### 3. 推送 Notion

```bash
python3 ~/.openclaw/skills/video-summarizer/scripts/push-to-notion.py \
    /tmp/video-summarizer/*/summary.md
```

---

## 核心流程

```
阶段一：素材准备 → metadata.json + *.vtt + video.mp4
阶段二：加工提炼 → screenshots/ + screenshot_urls.txt + AI 分析
阶段三：内容整合 → summary.md
阶段四：输出交付 → Notion 页面
```

**优势:** 断点续跑 · 分段优化 · 批量并行

---

## 📋 脚本清单

### 核心脚本（4 个）

| 脚本 | 功能 |
|------|------|
| `video-summarize.sh` | 主流程（Plan A/B 自动选择） |
| `upload-to-oss.py` | 上传截图到 OSS |
| `push-to-notion.py` | 推送 Notion |
| `analyze-subtitles-ai.py` | AI 分析生成总结 |

### 平台登录（2 个）

| 脚本 | 功能 |
|------|------|
| `bili-login.sh` | B 站扫码登录 |
| `douyin-login-v2.sh` | 抖音 Cookies 获取（浏览器读取） |

### 辅助工具（4 个）

| 脚本 | 功能 |
|------|------|
| `check-config.sh` | 检查配置是否就绪 |
| `convert-bili-cookie.py` | Cookies 格式转换 |
| `download-audio.sh` | Plan B: 音频下载 |
| `transcribe-audio.py` | Plan B: 语音转录 |

---

## 🎯 Plan A vs Plan B

| 项目 | Plan A | Plan B |
|-----|--------|--------|
| **字幕来源** | 平台官方字幕 | 语音转录 |
| **准确率** | 90%+ | 80-90% |
| **速度** | 快 (1-2 分钟) | 较慢 (3-5 分钟) |

### 各平台 Plan A/B 使用情况

| 平台 | Plan A | Plan B | 默认使用 | 说明 |
|------|--------|--------|----------|------|
| **Bilibili** | ✅ 官方 + 自动 | ✅ 备用 | Plan A | 推荐扫码登录获取官方字幕 |
| **YouTube** | ✅ 自动字幕 | ✅ 备用 | Plan A | 需网络可达 |
| **小红书** | ❌ 无 | ✅ 唯一 | Plan B | 依赖语音转录 |
| **抖音** | ❌ 无 | ✅ 唯一 | Plan B | 依赖语音转录 |

### Plan B 四层降级方案

```
1. Faster-Whisper (本地) → GPU/CPU 自适应
   ├─ GPU ≥8GB  → large-v2 模型
   ├─ GPU ≥4GB  → medium 模型
   ├─ GPU ≥2GB  → small 模型
   └─ 无 GPU    → base 模型 (CPU)

2. Groq API (whisper-large-v3) → 云端高速

3. 硅基流动 (FunAudioLLM/SenseVoiceSmall) → 备选云端

4. Whisper.cpp / OpenAI Whisper → 保底方案
```

**Plan B 配置**：
```bash
# ~/.openclaw/.env
GROQ_API_KEY=your_groq_api_key  # 语音转录 API（可选）
SILICONFLOW_API_KEY=your_key    # 硅基流动 API（可选）
```

---

## 🎬 平台专用流程

### 抖音平台流程

抖音无字幕支持，必须使用 Plan B 语音转录：

```
Step 1: 元数据 (douyin_downloader.py)
   ↓
┌─────┴─────┐
↓           ↓
Step 2:    Step 3:
Plan B     视频下载
转录       (douyin_downloader)
   ↓           ↓
   └─────┬─────┘
         ↓
Step 4: 文本 (audio.txt → transcript.txt)
   ↓
Step 5: AI 分析 (DashScope API)
   ↓
Step 6: 截图 (ffmpeg)
   ↓
Step 7: OSS 上传
   ↓
Step 8: Markdown 渲染
   ↓
Step 9: Notion 推送
```

**抖音 URL 格式支持：**
- `https://www.douyin.com/video/1234567890`
- `https://v.douyin.com/abc123/` (短链)
- `https://iesdouyin.com/share/video/1234567890`

**元数据输出（metadata.json）：**
```json
{
  "title": "视频标题",
  "uploader": "作者昵称",
  "uploader_id": "视频 ID",
  "duration": 0,
  "duration_string": "51:10",
  "thumbnail": "封面 URL",
  "webpage_url": "原始视频 URL",
  "platform": "douyin",
  "download_url": "无水印视频下载链接"
}
```

### B 站/YouTube 流程

支持 Plan A（官方字幕）优先：

```
Step 1: 元数据 (yt-dlp --dump-json)
   ↓
┌─────┴─────┐
↓           ↓
Step 2:    Step 3:
字幕       视频下载
(Cookies)  (yt-dlp)
   ↓           ↓
   └─────┬─────┘
         ↓
Step 4: 文本 (VTT → TXT)
   ↓
... (后续步骤相同)
```

---

## ✨ v0.1.5 新增特性

### 1. 并行优化
- **Step 2** (字幕下载) 和 **Step 4** (视频下载) 并行执行
- 节省约 **30 秒** (32%↓)
- 总耗时从 180 秒降至 150 秒

**并行实现：**
```bash
# 任务 A: 视频下载（后台）
(
    # 视频下载逻辑
) &
VIDEO_PID=$!

# 任务 B: 字幕处理（后台）
(
    # 字幕下载/转录逻辑
) &
SUBTITLE_PID=$!

# 等待两个任务完成
wait $VIDEO_PID
wait $SUBTITLE_PID
```

### 2. 标签提取策略

**四层策略:**
```
1. 标题 hashtag → #([\w\u4e00-\u9fa5]+)
2. 元数据 tags  → yt-dlp 提取的原始标签
3. AI 关键词    → AI 分析提取的核心概念
4. 默认值      → 视频总结/知识分享/学习
```

**标签规则:**
- 长度：2-15 字符 (兼容英文如 "openclaw")
- 数量：最多 5 个
- 去重：自动去重，保留唯一值

**Notion 解析:**
- 优先从 Markdown `**Tags:**` 行提取
- 格式：`**Tags:** `tag1` `tag2` `tag3``
- 回退到 `video_desc` 字段

### 3. GPU 自适应
- 自动检测 NVIDIA GPU 和显存
- 根据显存选择 Faster-Whisper 模型
- 无 GPU 时自动降级到 CPU 模式

### 4. 日志系统
- 新增日志级别：`log_info` / `log_warn` / `log_error` / `log_debug`
- 错误日志输出到 `$OUTPUT_DIR/error.log`
- 支持 `--verbose` 模式查看调试信息

---

## 📁 输出文件结构

```
output/
├── summary.md              # 📝 最终总结 (主要成果)
├── screenshot_urls.txt     # 🔗 截图 OSS 链接
├── metadata.json           # 📊 视频元数据
├── transcript.txt          # 📄 纯文本字幕
├── screenshots/            # 📸 截图原图 (本地备份)
└── *.log                   # 📋 日志文件 (verbose 模式)
```

---

## 📊 OSS 路径规范

**格式**: `/screenshots/<平台>/<视频 ID>_<时间戳>/<截图文件>`

**示例:**
```
screenshots/bilibili/BV1eTPEzNEqf_20260405_053203/screenshot_01.jpg
screenshots/douyin/7234567890_20260405_175010/chapter_01.jpg
screenshots/xhs/69c1493b000000002003b3ce_20260405_152852/screenshot_01.jpg
screenshots/youtube/dQw4w9WgXcQ_20260405_120000/screenshot_01.jpg
```

**关键点:**
- ✅ 路径必须包含时间戳，避免重复视频覆盖
- ✅ `upload-to-oss.py auto` 模式自动生成正确路径
- ✅ `summary.md` 渲染前需确保 `screenshot_urls.txt` 已更新
- ✅ OSS Bucket 必须公开可读（直接 URL 访问）

---

## ⚙️ 配置（`~/.openclaw/.env`）

```bash
# OSS 图床（必需）
ALIYUN_OSS_AK=your_access_key_id
ALIYUN_OSS_SK=your_access_key_secret
ALIYUN_OSS_BUCKET_ID=your_bucket_name
ALIYUN_OSS_ENDPOINT=oss-cn-shanghai.aliyuncs.com

# Notion（可选，自动推送时需要）
NOTION_API_KEY=your_notion_api_key
NOTION_VIDEO_SUMMARY_DATABASE_ID=your_database_id

# AI 分析（必需）
DASHSCOPE_API_KEY=your_dashscope_api_key

# Plan B 语音转录（可选）
GROQ_API_KEY=your_groq_api_key
SILICONFLOW_API_KEY=your_siliconflow_api_key

# 本地 Whisper（可选）
WHISPER_MODEL=base  # tiny/base/small/medium/large
USE_LOCAL_WHISPER=false  # true 强制使用本地 Whisper
```

### 平台 Cookies 要求

| 平台 | Cookies 文件 | 必需 | 获取方式 |
|------|-------------|------|----------|
| B 站 | `~/.cookies/bilibili_cookies.txt` | 推荐 | `bili-login.sh` 扫码 |
| 抖音 | `~/.cookies/douyin_cookies.txt` | ❌ | 专用下载器无需 Cookies |
| 小红书 | `~/.cookies/xiaohongshu_cookies.txt` | ❌ | Plan B 无需 Cookies |
| YouTube | `~/.cookies/youtube_cookies.txt` | ❌ | 自动字幕无需 Cookies |

---

## 📋 命令行选项

| 选项 | 说明 | 默认 |
|------|------|------|
| `--verbose`, `-v` | 详细日志 | 关闭 |
| `--keep-video` | 保留视频/音频 | 清理 |
| `--push` | 自动推送 Notion | 手动 |
| `--resume` | 从中断恢复 | 从头开始 |

---

## 📝 输出格式（summary.md）

1. **标题 + Tags + Author**
2. **📝 Note** — AI 概述
3. **📺 视频信息** — 链接/时长/播放数据
4. **📚 关键概念** — 术语表格（按时间排序）
5. **🎯 核心要点** — emoji+ 描述 + 时间戳
6. **🎬 视频章节** — 标题 + 时间轴 + 截图
7. **⚠️ 注意事项** — 特别提醒
8. **💡 总结** — AI 归纳

---

## 🔧 故障排查

### Cookies 过期

```bash
# 扫码更新
./bili-login.sh
```

### 配置检查

```bash
# 运行检查
./check-config.sh
```

### 查看详细日志

```bash
# 使用 verbose 模式
./video-summarize.sh "URL" /tmp/output --verbose

# 查看日志文件
cat /tmp/output/error.log          # 错误日志
cat /tmp/output/oss_upload.log     # OSS 上传日志
cat /tmp/output/ai_analysis.log    # AI 分析日志
```

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 截图 404 | OSS 路径不匹配 | 使用 `upload-to-oss.py auto` 重新上传 |
| 标签默认值 | 标签提取失败 | 检查标题 hashtag 格式 `#标签` |
| 转录失败 | 无 GPU/API 配额 | 检查 `GROQ_API_KEY` 或 `SILICONFLOW_API_KEY` |
| Notion 推送失败 | API Key 过期 | 更新 `NOTION_API_KEY` |
| 并行任务失败 | 依赖缺失 | 检查 `ffmpeg` / `yt-dlp` 安装 |

---

## 📂 项目文件结构

```
video-summarizer/
├── SKILL.md                  # 完整技能文档 (本文档)
├── README.md                 # 快速入门
├── CHANGELOG.md              # 版本变更日志
├── CODE_AUDIT_20260405.md    # v0.1.5 代码审计报告
├── prompt.json               # AI 提示词配置
├── scripts/                  # 核心脚本
│   ├── video-summarize.sh    # 主流程 (Plan A/B 自动，并行优化)
│   ├── upload-to-oss.py      # OSS 图床上传 (截图 + 封面)
│   ├── push-to-notion.py     # Notion 推送 (标签解析)
│   ├── analyze-subtitles-ai.py # AI 分析 + Markdown 渲染 (标签提取)
│   ├── download-audio.sh     # Plan B: 音频下载
│   ├── transcribe-audio.py   # Plan B: 语音转录 (GPU 自适应)
│   ├── check-config.sh       # 配置检查
│   ├── bili-login.sh         # B 站扫码登录
│   └── douyin_downloader.py  # 抖音专用下载工具 (无需 Cookies)
└── templates/
    └── summary.md            # 总结文档模板
```

**说明:**
- ✅ `scripts/` 目录包含所有核心脚本，均为可执行文件 (755)
- ✅ `templates/` 目录包含 Markdown 模板
- ✅ `douyin_downloader.py` 为抖音专用下载器，无需 Cookies
- ✅ `bili-login.sh` 仅 B 站需要，其他平台无需登录

---

## 🔜 后续优化方向

### v0.1.6 计划

**高优先级:**
- [ ] 重构 `push-to-notion.py`（提取平台分支为独立函数）
- [ ] 添加单元测试（核心函数覆盖率 80%+）
- [ ] 完善错误处理和日志（结构化日志格式）

**中优先级:**
- [ ] 性能优化（截图并行上传、结果缓存）
- [ ] 文档完善（API 参考、故障排查手册）

**低优先级:**
- [ ] 支持更多平台（TikTok、Instagram Reels）
- [ ] Web UI（可选）

---

## 📞 更多文档

- **快速入门:** [README.md](README.md) - 快速开始、命令行选项
- **变更日志:** [CHANGELOG.md](CHANGELOG.md) - 版本历史
- **提示词配置:** [prompt.json](prompt.json) - AI 分析参数
- **代码审计:** [CODE_AUDIT_20260405.md](CODE_AUDIT_20260405.md) - v0.1.5 代码审计报告

---

**维护人:** Ajay Hao  
**文档:** `~/.openclaw/skills/video-summarizer/SKILL.md`  
**版本:** v0.1.5  
**发布日期:** 2026-04-05
