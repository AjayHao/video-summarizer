# Video Summarizer — 视频总结生成技能

将 B 站/YouTube 视频转换为结构化 Notion 总结文档，自动上传截图，一键推送 Notion。

**版本:** v0.1.2  
**最后更新:** 2026-04-04  
**状态:** ✅ 步骤顺序优化 · Bug 修复 · 断点续跑 · 截图嵌入（30 张）

---

## 平台支持状态

| 平台 | 支持状态 | 字幕支持 | Plan B 语音转录 | 说明 |
|------|----------|----------|----------------|------|
| **Bilibili** | ✅ 完整支持 | ✅ 官方 + 自动 | ✅ 支持 | 推荐扫码登录获取 Cookies |
| **YouTube** | ✅ 完整支持 | ✅ 自动字幕 | ✅ 支持 | 需网络可达 |
| **小红书** | 🚧 待完善 | ⚠️ 部分视频 | ✅ 支持 | 需优化视频下载稳定性 |
| **抖音** | 🚧 待完善 | ⚠️ 部分视频 | ✅ 支持 | 需优化视频下载稳定性 |
| **微信视频号** | 🚧 待完善 | ❌ 无字幕 | ✅ 支持 | 依赖 Plan B 语音转录 |

---

## 快速开始

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

## 脚本清单

| 脚本 | 功能 |
|------|------|
| `video-summarize.sh` | 主流程（Plan A/B 自动选择） |
| `upload-to-oss.py` | 上传截图到 OSS |
| `push-to-notion.py` | 推送 Notion |
| `analyze-subtitles-ai.py` | AI 分析生成总结 |
| `bili-login.sh` | B 站扫码登录 |
| `check-config.sh` | 检查配置 |

---

## Plan A vs Plan B

| 项目 | Plan A | Plan B |
|-----|--------|--------|
| **字幕来源** | 平台官方字幕 | 语音转录 |
| **准确率** | 90%+ | 80-90% |
| **速度** | 快 | 较慢 |

---

## 配置（`~/.openclaw/.env`）

```bash
# OSS 图床
ALIYUN_OSS_AK=your_access_key_id
ALIYUN_OSS_SK=your_access_key_secret
ALIYUN_OSS_BUCKET_ID=your_bucket_name

# Notion
NOTION_API_KEY=your_notion_api_key
NOTION_VIDEO_SUMMARY_DATABASE_ID=your_database_id

# AI 分析
DASHSCOPE_API_KEY=your_dashscope_api_key

# Plan B 可选
GROQ_API_KEY=your_groq_api_key
```

---

## 命令行选项

| 选项 | 说明 |
|------|------|
| `--verbose` | 详细日志 |
| `--keep-video` | 保留视频文件 |
| `--resume` | 断点续跑 |

---

## 输出格式（summary.md）

1. **标题 + Tags + Author**
2. **📝 Note** — AI 概述
3. **📺 视频信息** — 链接/时长/播放数据
4. **📚 关键概念** — 术语表格（按时间排序）
5. **🎯 核心要点** — emoji+ 描述 + 时间戳（无截图）
6. **🎬 视频章节** — 标题 + 时间轴 + 截图
7. **⚠️ 注意事项** — 特别提醒（无截图）
8. **💡 总结** — AI 归纳

---

## 依赖

```bash
# 必需
yt-dlp, ffmpeg, python3, requests, oss2

# 安装
pip3 install requests oss2 python-dotenv
```

---

## 故障排查

```bash
# 检查配置
~/.openclaw/skills/video-summarizer/scripts/check-config.sh

# 详细日志
./video-summarize.sh "URL" --verbose

# 断点续跑
./video-summarize.sh "URL" --resume

# Cookies 过期
~/.openclaw/skills/video-summarizer/scripts/bili-login.sh
```

---

## 后续优化方向

### 阶段一
- [ ] 更多平台（快手、视频号）
- [ ] 短链解析优化
- [ ] 代理支持

### 阶段二
- [ ] 截图智能选择（画面变化检测）
- [ ] AI 提示词优化
- [ ] 本地大模型支持

### 阶段三
- [ ] 多模板支持
- [ ] 模板变量扩展
- [ ] 多格式输出

### 阶段四
- [ ] 更多目标平台（语雀、飞书）
- [ ] 批量推送优化
- [ ] 自动重试机制

---

**维护人:** Ajay Hao  
**文档:** ~/.openclaw/skills/video-summarizer/SKILL.md
