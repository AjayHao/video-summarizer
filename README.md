# Video Summarizer

🎬 将 B 站/YouTube/小红书/抖音视频转换为结构化 Notion 风格总结

**版本:** v0.1.3  
**支持:** Plan A (字幕) + Plan B (语音转录)
**更新:** 2026-04-04 - 多平台支持 & 封面图上传

---

## 平台支持状态

| 平台 | 支持状态 | 字幕支持 | Plan B 语音转录 | 备注 |
|------|----------|----------|----------------|------|
| **Bilibili** | ✅ 完整支持 | ✅ 官方 + 自动 | ✅ 支持 | 推荐扫码登录获取 Cookies |
| **YouTube** | ✅ 完整支持 | ✅ 自动字幕 | ✅ 支持 | 需网络可达 |
| **小红书** | ✅ 基本支持 | ❌ 无字幕 | ✅ 支持 | 依赖 Plan B 语音转录（已优化下载 + 封面上传） |
| **抖音** | 🚧 脚本就绪 | ❌ 无字幕 | ✅ 支持 | 等待反爬解除后测试 |
| **微信视频号** | 🚧 待测试 | ❌ 无字幕 | ✅ 支持 | 依赖 Plan B 语音转录 |

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

### 4. 推送到 Notion

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
| **微信视频号** | ❌ 无 | ✅ 唯一 | Plan B |

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

格式:`/screenshots/<平台>/<视频 ID>_<时间戳>/`

| 平台 | 示例 |
|------|------|
| bilibili | `/screenshots/bilibili/BV1eTPEzNEqf_20260326_010000/` |
| douyin | `/screenshots/douyin/7234567890_20260326_010000/` |
| xhs | `/screenshots/xhs/abc123_20260326_010000/` |
| youtube | `/screenshots/youtube/dQw4w9WgXcQ_20260326_010000/` |
| wxvideo | `/screenshots/wxvideo/123456_20260326_010000/` |

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
cat /tmp/output/oss_upload.log
cat /tmp/output/ai_analysis.log
```

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
├── prompt.json               # AI 提示词配置
├── scripts/
│   ├── video-summarize.sh    # 主流程 (Plan A/B 自动)
│   ├── upload-to-oss.py      # OSS 图床上传
│   ├── push-to-notion.py     # Notion 推送
│   ├── analyze-subtitles-ai.py # AI 分析
│   ├── download-audio.sh     # Plan B: 音频下载
│   ├── transcribe-audio.py   # Plan B: 语音转录
│   ├── check-config.sh       # 配置检查
│   ├── bili-login.sh         # B 站扫码登录
│   ├── douyin-login-v2.sh    # 抖音 Cookies 获取
│   └── convert-bili-cookie.py # Cookies 格式转换
└── templates/
    ├── summary.md            # 总结文档模板
    └── README.md             # 模板使用说明
```

---

## 📞 更多文档

- **技能文档:** [SKILL.md](SKILL.md) - 完整架构、配置详解、优化方向
- **提示词配置:** [prompt.json](prompt.json) - AI 分析参数
- **模板说明:** [templates/README.md](templates/README.md) - 模板变量详解

---

**版本:** v0.1.3
**发布:** 2026-04-04
**维护人:** Ajay Hao
