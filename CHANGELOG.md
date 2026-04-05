# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
