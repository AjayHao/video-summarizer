# Video Summarizer

🎬 将 B 站/YouTube/小红书/抖音视频转换为结构化 Notion 风格总结

**版本:** v0.1.5  
**支持:** Plan A (字幕) + Plan B (语音转录)
**更新:** 2026-04-05 - 并行优化 & 标签提取 & OSS 路径修复 & GPU 自适应

---

## 平台支持状态

| 平台 | 支持状态 | 字幕支持 | Plan B 语音转录 | 备注 |
|------|----------|----------|----------------|------|
| **Bilibili** | ✅ 完整支持 | ✅ 官方 + 自动 | ✅ 支持 | 推荐扫码登录获取 Cookies |
| **YouTube** | ✅ 完整支持 | ✅ 自动字幕 | ✅ 支持 | 需网络可达 |
| **小红书** | ✅ 基本支持 | ❌ 无字幕 | ✅ 支持 | 依赖 Plan B 语音转录（已优化下载 + 封面上传） |
| **抖音** | ✅ 完整支持 | ❌ 无字幕 | ✅ 支持 | 使用专用下载工具（无需 Cookies） |

---

## 🏗️ 架构概览

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

### 核心特性

- ✅ **断点续跑** - `.progress.json` 记录进度，`--resume` 恢复
- ✅ **并行优化** - Step 2+3 并行，节省 32% 时间
- ✅ **Plan A/B** - 字幕优先，语音转录兜底
- ✅ **GPU 自适应** - 根据显存自动选择 Whisper 模型
- ✅ **四层标签** - 标题 hashtag → 元数据 → AI → 默认
- ✅ **OSS 图床** - 永久有效截图链接，避免防盗链

---

## 🚀 快速开始

### 1. 扫码登录 (首次使用)

```bash
# 获取 B 站 Cookies
~/.openclaw/skills/video-summarizer/scripts/bili-login.sh

# 扫码后 Cookies 有效期约 90 天
```

### 2. 检查配置

```bash
# 检查所有配置是否就绪
~/.openclaw/skills/video-summarizer/scripts/check-config.sh
```

### 3. 处理视频

```bash
# 基础用法
~/.openclaw/skills/video-summarizer/scripts/video-summarize.sh \
    "视频 URL" \
    /tmp/output

# 详细日志模式
~/.openclaw/skills/video-summarizer/scripts/video-summarize.sh \
    "视频 URL" \
    /tmp/output \
    --verbose

# 保留视频文件
~/.openclaw/skills/video-summarizer/scripts/video-summarize.sh \
    "视频 URL" \
    /tmp/output \
    --keep-video

# 自动推送到 Notion
~/.openclaw/skills/video-summarizer/scripts/video-summarize.sh \
    "视频 URL" \
    /tmp/output \
    --push

# 从中断点恢复
~/.openclaw/skills/video-summarizer/scripts/video-summarize.sh \
    "视频 URL" \
    /tmp/output \
    --resume
```

### 4. 手动推送到 Notion

```bash
python3 ~/.openclaw/skills/video-summarizer/scripts/push-to-notion.py \
    /tmp/output/summary.md
```

---

## 📋 命令行选项

| 选项 | 说明 | 默认 |
|------|------|------|
| `--verbose`, `-v` | 详细日志 | 关闭 |
| `--keep-video` | 保留视频/音频 | 清理 |
| `--push` | 自动推送 Notion | 手动 |
| `--resume` | 从中断恢复 | 从头开始 |

---

## 🎯 Plan A vs Plan B

### 对比表

| | Plan A | Plan B |
|--|--------|--------|
| **触发** | 有字幕 | 无字幕 |
| **来源** | 官方/自动字幕 | 语音转录 |
| **速度** | 快 (1-2 分钟) | 较慢 (3-5 分钟) |
| **准确率** | 高 (90%+) | 中 (80-90%) |

### 各平台使用情况

| 平台 | Plan A | Plan B | 默认 |
|------|--------|--------|------|
| **Bilibili** | ✅ 官方 + 自动 | ✅ 备用 | Plan A |
| **YouTube** | ✅ 自动字幕 | ✅ 备用 | Plan A |
| **小红书** | ❌ 无 | ✅ 唯一 | Plan B |
| **抖音** | ❌ 无 | ✅ 唯一 | Plan B |

### Plan B 四层降级方案

```transcribe-audio.py
1. Faster-Whisper (本地) → GPU/CPU 自适应
   ├─ GPU ≥8GB  → large-v2 模型
   ├─ GPU ≥4GB  → medium 模型
   ├─ GPU ≥2GB  → small 模型
   └─ 无 GPU    → base 模型 (CPU)

2. Groq API (whisper-large-v3) → 云端高速

3. 硅基流动 (FunAudioLLM/SenseVoiceSmall) → 备选云端

4. Whisper.cpp / OpenAI Whisper → 保底方案
```


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

### 截图路径

**格式:** `/screenshots/<平台>/<视频 ID>_<时间戳>/<截图文件>`

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

### 封面路径

**格式:** `/covers/<平台>/<视频 ID>_<时间戳>/cover.jpg`

**示例:**
```
covers/bilibili/BV1eTPEzNEqf_20260405_053203/cover.jpg
covers/douyin/7234567890_20260405_175010/cover.jpg
covers/xhs/69c1493b000000002003b3ce_20260405_152852/cover.jpg
covers/youtube/dQw4w9WgXcQ_20260405_120000/cover.jpg
```

**关键点:**
- ✅ 封面单独上传到 `/covers/` 目录，与截图分离
- ✅ 封面文件名统一为 `cover.jpg`
- ✅ 封面路径同样包含时间戳，避免覆盖
- ✅ 封面上传由 `upload-to-oss.py thumbnail` 模式处理

### 平台支持矩阵

| 功能 | B 站 | YouTube | 小红书 | 抖音 |
|------|------|---------|--------|------|
| 元数据获取 | ✅ | ✅ | ✅ | ✅ (专用) |
| 官方字幕 | ✅ | ✅ | ❌ | ❌ |
| Plan B 转录 | ✅ | ✅ | ✅ | ✅ |
| 视频下载 | ✅ | ✅ | ✅ | ✅ |
| 截图生成 | ✅ | ✅ | ✅ | ✅ |
| OSS 上传 | ✅ | ✅ | ✅ | ✅ |
| Notion 推送 | ✅ | ✅ | ✅ | ✅ |
| Cookies 要求 | 推荐 | ❌ | ❌ | ❌ |


---

## ✨ v0.1.5 新增特性

### 1. 并行优化
- **Step 2** (字幕下载) 和 **Step 4** (视频下载) 并行执行
- 节省约 **30 秒** (32%↓)
- 总耗时从 180 秒降至 150 秒

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

## 🎬 抖音平台专用流程

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

## 🎨 模板修改

**位置:** `templates/summary.md`

**示例：添加新章节**

```markdown
## 🆕 新增章节

这里是新章节内容...

---
```

**测试:**

```bash
./video-summarize.sh "URL" /tmp/test
cat /tmp/test/summary.md
```

---

## 📂 项目文件结构

```
video-summarizer/
├── SKILL.md                  # 完整技能文档
├── README.md                 # 快速入门 (本文档)
├── CHANGELOG.md              # 版本变更日志
├── CODE_AUDIT_20260405.md    # 代码审计报告
├── prompt.json               # AI 提示词配置
├── scripts/                  # 核心脚本
│   ├── video-summarize.sh    # 主流程 (Plan A/B 自动)
│   ├── upload-to-oss.py      # OSS 图床上传 (截图 + 封面)
│   ├── push-to-notion.py     # Notion 推送
│   ├── analyze-subtitles-ai.py # AI 分析 + Markdown 渲染
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

## 📞 更多文档

- **技能文档:** [SKILL.md](SKILL.md) - 完整架构、配置详解、平台流程
- **变更日志:** [CHANGELOG.md](CHANGELOG.md) - 版本历史
- **提示词配置:** [prompt.json](prompt.json) - AI 分析参数
- **代码审计:** [CODE_AUDIT_20260405.md](CODE_AUDIT_20260405.md) - v0.1.5 代码审计报告

---

**版本:** v0.1.5  
**发布:** 2026-04-05  
**维护人:** Ajay Hao
