# Changelog

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
- 路径规范：截图 `/screenshots/`，封面 `/covers/`
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

---

**发布说明**: v1.0.0 是首个稳定版本，适用于生产环境。
