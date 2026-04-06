# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.4] - 2026-04-06

### ✨ 新增功能

**抖音渠道发布时间提取**:
- 新增 `--json` 参数到 `douyin_downloader.py`，输出结构化元数据
- 从抖音 API 响应中提取 `create_time` 时间戳
- 自动转换为 `upload_date` (YYYYMMDD 格式)
- 支持 `modal_id` 格式的视频链接（课程/精选视频）

**小红书渠道发布时间提取**:
- 从笔记 ID 前 8 位 hex 解析时间戳
- 自动转换为 `upload_date` (YYYYMMDD 格式)
- 兼容短链和完整链接格式

### 🐛 Bug 修复

**小红书/YouTube 视频下载失败处理**:
- 修复 yt-dlp 下载失败但脚本未检测到的问题
- 新增视频文件存在性检查，避免后续步骤失败
- 截图步骤支持封面图降级方案（无视频时使用封面图代替）
- 优化错误日志输出，便于排查问题

**小红书视频下载容错增强**:
- 新增两级下载策略，兼容不同视频格式类型
  - 策略 1：优先尝试分片格式（适用于 B 站/YouTube/部分小红书视频）
  - 策略 2：分片格式失败后自动降级到单文件格式（适用于小红书单流媒体）
- 解决小红书部分视频 `Requested format is not available` 错误
- 每级策略最多重试 3 次，确保下载稳定性

**小红书 Author 信息未写入 Notion**:
- 修复 `metadata.get('uploader', '')` 无法处理 `None` 的问题
- 改用 `metadata.get('uploader') or metadata.get('uploader_id', '')`
- 16 进制 ID 自动转换为 "小红书用户"

**抖音元数据解析编码问题**:
- 改用 JSON 解析抖音元数据（避免 bash 解析中文编码问题）
- 正确提取 `video_id`、`upload_date`、`uploader_id` 等字段
- 支持多种抖音链接格式（`/video/`、`?modal_id=`、短链）

### 📝 文档更新

**依赖版本要求补充**:
- ffmpeg: 最低版本 >= 6.1
- yt-dlp: 最低版本 >= 2026.03.17
- 更新 SKILL.md、README.md、故障排查表格

**版本号统一**:
- 所有脚本、文档、配置文件统一为 v1.0.4
- 发布日期更新为 2026-04-06

### 📊 变更统计

- 修改文件：8 个
- 新增代码：+124 行
- 删除代码：-21 行

### ✅ 核心平台（4 个）

- **Bilibili（B 站）** - 完整支持
- **YouTube** - 完整支持
- **小红书** - 基本支持（语音转录）
- **抖音** - 完整支持（专用下载器）

## [1.0.3] - 2026-04-06

### 🗑️ 平台精简

**移除微信视频号支持**:
- 微信视频号已不支持外链访问，移除相关代码
- 删除 `wxvideo` 平台判断逻辑
- 精简 `push-to-notion.py` 微信分支代码
- 删除 `video-summarize.sh` 微信 ID 提取逻辑

### 📝 文档更新

- 版本号统一更新为 1.0.3
- 发布日期更新为 2026-04-06
- 模板文件版本同步更新

### ✅ 核心平台（4 个）

- Bilibili（B 站）
- YouTube
- 小红书
- 抖音

---

## [1.0.2] - 2026-04-06

### 🐛 Bug 修复

**OSS 路径规范修正**:
- 截图路径添加时间戳，避免同视频多次运行覆盖旧文件
  - 格式：`/screenshots/<平台>/<视频 ID>_<时间戳>/`
- 封面路径独立到 `/thumbnails/` 目录，不含时间戳
  - 格式：`/thumbnails/<平台>/<视频 ID>/cover.jpg`

### 📝 文档更新

- `SKILL.md`: 更新封面路径示例
- `CHANGELOG.md`: 修正封面目录名称（`/covers/` → `/thumbnails/`）
- `scripts/upload-to-oss.py`: 更新注释说明

---

## [1.0.1] - 2026-04-05

### 🐛 Bug 修复

**Notion 数据库配置修正**:
- 修正 SKILL.md 中 Notion 数据库属性说明（与 push-to-notion.py 代码一致）
- 字段名变更：`Name` → `Title`
- 字段类型修正：`Source` 从 `select` 改为 `rich_text`
- 新增字段说明：`PubDate`、`Length`、`Cover`、`ts`

### 📝 文档更新

**SKILL.md - Notion 数据库配置部分**:
- 完整 9 个属性说明（类型、来源、格式）
- 配置步骤详解（Database ID 获取方法）
- 数据库视图示例

**完整属性清单**:
| 属性名 | 类型 | 说明 |
|--------|------|------|
| Title | `title` | 视频标题（≤200 字符） |
| Source | `rich_text` | 平台来源 |
| Author | `rich_text` | UP 主/作者 |
| Url | `url` | 视频链接 |
| Tags | `multi_select` | 标签（最多 5 个） |
| PubDate | `date` | 发布日期 |
| Length | `rich_text` | 视频时长（MM:SS 格式） |
| Cover | `files` | 封面图片（可选，外部 URL） |
| ts | `date` | 创建时间戳（ISO 8601，东八区 +08:00） |

---

## [1.0.0] - 2026-04-05

### 🎉 正式发布

Video Summarizer OpenClaw Skill v1.0.0 正式发布！

### ✨ 核心功能

**多平台支持**:
- ✅ Bilibili - 完整支持（官方字幕 + 语音转录）
- ✅ YouTube - 完整支持（自动字幕 + 语音转录）
- ✅ 小红书 - 基本支持（语音转录）
- ✅ 抖音 - 完整支持（专用下载器，无需 Cookies）

**智能处理**:
- Plan A/B 双模式：官方字幕优先，语音转录兜底
- AI 分析：提取关键概念、核心要点、注意事项
- 截图嵌入：基于 AI 分析结果自动生成关键帧截图
- 四层标签策略：标题 hashtag → 元数据 → AI 关键词 → 默认值

**性能优化**:
- 并行执行：字幕下载与视频下载并行，节省 32% 时间
- GPU 自适应：自动检测显存，选择最优 Whisper 模型
- 断点续跑：支持从中断点恢复

**图床集成**:
- 阿里云 OSS 自动上传
- 路径规范：截图 `/screenshots/`，封面 `/thumbnails/`
- 永久链接，支持 Notion 嵌入

**一键推送**:
- 自动推送 Notion 数据库
- 标签解析：从 Markdown `**Tags:**` 行提取

### 🔧 技术特性

**转录方案**:
1. Faster-Whisper（本地 GPU/CPU 自适应）
2. Groq API（whisper-large-v3，云端高速）
3. 硅基流动（FunAudioLLM/SenseVoiceSmall，备选）
4. Whisper.cpp / OpenAI Whisper（保底）

**日志系统**:
- 分级日志：log_info / log_warn / log_error / log_debug
- 错误日志：`$OUTPUT_DIR/error.log`
- Verbose 模式：`--verbose` 查看详细日志

### 📋 配置要求

**必需**:
- 阿里云 OSS（AK/SK/Bucket/Endpoint）
- DashScope API Key（AI 分析）

**可选**:
- Notion API Key + Database ID（自动推送）
- Groq API Key（语音转录加速）
- NVIDIA GPU（本地转录加速）

### 📝 文档重构

- README.md：快速入门（5 分钟上手）
- SKILL.md：完整技能文档（平台配置、架构说明、故障排查）
- 删除过程文档（CODE_AUDIT、docs/ 目录）

---

## 历史版本（已归档）

v1.0.0 之前的 0.1.x 版本为开发过程版本，功能已整合到 v1.0.0。

如需查看完整版本历史，请参考 Git 提交记录：
https://github.com/AjayHao/video-summarizer/commits/main
