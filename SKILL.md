# Video Summarizer — 视频总结生成技能

将 B 站/YouTube/抖音等视频内容转换为结构化的 Notion 风格总结文档，自动上传截图到图床，一键推送到 Notion 知识库。

**版本:** v2.0  
**最后更新:** 2026-03-25  
**状态:** ✅ 完整流程已验证（Plan A + OSS 图床 + Notion 推送）

---

## 核心功能

自动完成：`视频 URL → 元数据 → 字幕 → 截图 → 结构化总结 → OSS 图床 → Notion 推送`

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Video Summarizer v2.0 完整流程                    │
├─────────────────────────────────────────────────────────────────────┤
│  Step 1: 获取元数据 (yt-dlp --dump-json)                            │
│         ↓                                                           │
│  Step 2: 下载字幕 (Cookies → 官方字幕 / 自动字幕)                    │
│         ↓                                                           │
│  Step 3: 分析字幕内容 (awk 提取纯文本)                               │
│         ↓                                                           │
│  Step 4: 下载视频 (3 次重试 + 降级，必须成功)                         │
│         ↓                                                           │
│  Step 5: 智能截图 (根据时长，1-7 张)                                  │
│         ↓                                                           │
│  Step 6: 上传截图到阿里云 OSS 图床 (永久链接)                         │
│         ↓                                                           │
│  Step 7: AI 智能分析生成结构化总结                                    │
│         ↓                                                           │
│  Step 8: 推送预览 → 老大审阅确认                                     │
│         ↓                                                           │
│  Step 9: 一键推送到 Notion 知识库                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Plan A 完整流程（字幕可用）

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: 获取元数据 (yt-dlp --dump-json)                    │
│         ↓                                                   │
│  Step 2: 下载字幕 (Cookies → 自动)                          │
│         ↓                                                   │
│  Step 3: 分析字幕内容 (awk 提取纯文本)                       │
│         ↓                                                   │
│  Step 4: 下载视频 (3 次重试 + 降级，必须成功)                │
│         ↓                                                   │
│  Step 5: 智能截图 (根据时长，1-7 张)                         │
│         ↓                                                   │
│  Step 6: 上传截图到阿里云 OSS (永久链接)                     │
│         ↓                                                   │
│  Step 7: AI 分析生成结构化总结                                │
│         ↓                                                   │
│  Step 8: 推送到 Notion 知识库                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Plan B 流程（字幕不可用）

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1-2: 字幕下载失败                                     │
│         ↓                                                   │
│  Plan B: 语音转录                                           │
│         ↓                                                   │
│  下载音频 (3 级降级：分离音轨 → 转换 → 视频提取)              │
│         ↓                                                   │
│  Whisper 转录 (本地或 API)                                   │
│         ↓                                                   │
│  继续 Plan A Step 3-8                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 使用方法

### 🚀 推荐：完整流程（Plan A + OSS + Notion）

```bash
# 使用 Cookies（获取官方字幕）+ 阿里云 OSS 图床
~/.openclaw/skills/video-summarizer/scripts/video-summarize-oss.sh \
    "https://www.bilibili.com/video/BVxxx" \
    /tmp/output \
    ~/.cookies/bilibili_cookies.txt

# 无 Cookies（尝试自动字幕）
~/.openclaw/skills/video-summarizer/scripts/video-summarize-oss.sh \
    "https://www.bilibili.com/video/BVxxx" \
    /tmp/output
```

### 📝 单独推送已生成的总结到 Notion

```bash
python3 ~/.openclaw/skills/video-summarizer/scripts/push-to-notion.py \
    /tmp/output/summary-ai.md \
    [Notion Database ID]  # 可选，省略则使用 .env 中配置的默认值
```

### 📤 最后一步：推送预览 + 确认

```bash
# 生成推送预览，等待老大确认
~/.openclaw/skills/video-summarizer/scripts/finalize-and-push.sh \
    /tmp/output
```

### Plan B: 单独下载音频（用于转录）

```bash
# 下载音频（带重试和降级）
~/.openclaw/skills/video-summarizer/scripts/download-audio.sh \
    "https://www.bilibili.com/video/BVxxx" \
    /tmp/audio.mp3
```

### 分析字幕生成总结

```bash
# 从字幕生成结构化总结
python3 ~/.openclaw/skills/video-summarizer/scripts/analyze-subtitles.py \
    /tmp/output/video.zh-Hans.vtt \
    /tmp/output/metadata.json \
    /tmp/output/summary.md
```

---

## 脚本清单

| 脚本 | 功能 | 说明 |
|------|------|------|
| `video-summarize-oss.sh` | 完整流程（推荐） | Plan A + OSS 图床 + 推送预览 |
| `video-summarize.sh` | 基础流程 | 不含图床，截图保存在本地 |
| `push-to-notion.py` | Notion 推送 | 将总结推送到 Notion Database |
| `finalize-and-push.sh` | 推送预览 | 生成预览，等待确认 |
| `upload-to-oss.py` | OSS 上传 | 单文件/批量上传到阿里云 OSS |
| `upload-to-qiniu.py` | 七牛上传 | 备选图床方案 |
| `analyze-subtitles-ai.py` | AI 分析 | 从字幕生成结构化总结 |
| `analyze-subtitles.py` | 基础分析 | 不含 AI 的总结生成 |
| `download-audio.sh` | 音频下载 | Plan B 专用 |

---

## 容错机制

### Plan A: 字幕获取优先级

| 优先级 | 方式 | 说明 |
|--------|------|------|
| 1️⃣ | Cookies + 官方字幕 | 最准确，需 B 站登录 |
| 2️⃣ | 自动字幕 | 无需登录，部分视频支持 |

### Plan A: 视频下载策略

| 重试 | 策略 | 说明 |
|------|------|------|
| 第 1 次 | 720P 视频 + 音频 | 标准质量 |
| 第 2 次 | 720P 视频 + 音频 | 重试 |
| 第 3 次 | 720P 视频 + 音频 | 重试 |
| 降级 | 任意可用格式 | 最后尝试 |

### Plan B: 音频下载降级

```
尝试 1: 直接下载分离音轨 (最快，5-7MB)
   ↓ 失败
尝试 2: 下载并转换音频 (重试 1 次)
   ↓ 失败
尝试 3: 下载视频并提取音频 (降级，最慢)
   ↓ 失败
报错退出
```

### OSS 上传容错

- 自动检测配置文件，未配置时降级为本地存储
- 批量上传时记录失败文件，不影响其他文件
- 支持签名 URL（私有 Bucket）和公开 URL（公开 Bucket）

---

## 输出结构

```
output/
├── metadata.json          # 视频元数据
├── video.mp4              # 视频文件
├── video.zh-Hans.vtt      # 字幕文件（或 audio.vtt）
├── transcript.txt         # 纯文本字幕
├── summary.md             # 基础结构化总结
├── summary-ai.md          # AI 增强版总结（推荐）
├── PUSH_PREVIEW.txt       # 推送预览文本
├── screenshots/
│   ├── screenshot_01.jpg  # 视频帧截图（本地备份）
│   ├── screenshot_02.jpg
│   └── ...
└── screenshots_oss/       # OSS 上传记录（可选）
    └── urls.txt           # OSS 链接列表
```

---

## 配置选项

### 环境变量（`~/.openclaw/.env`）

```bash
# ==================== 阿里云 OSS 图床 ====================
ALIYUN_OSS_AK=your_access_key_id
ALIYUN_OSS_SK=your_access_key_secret
ALIYUN_OSS_BUCKET_ID=your_bucket_name
ALIYUN_OSS_ENDPOINT=oss-cn-shanghai.aliyuncs.com

# ==================== Notion 推送 ====================
NOTION_API_KEY=your_notion_api_key
NOTION_VIDEO_SUMMARY_DATABASE_ID=your_database_id

# ==================== 可选配置 ====================
# Whisper API Key（Plan B 使用 Groq API）
WHISPER_API_KEY=your_groq_key

# 自定义 Cookies 路径
BILIBILI_COOKIES=~/.cookies/bilibili_cookies.txt

# 自动推送到 Notion（true/false）
AUTO_PUSH_TO_NOTION=false
```

### 截图策略

| 视频时长 | 截图数量 | 间隔 |
|----------|----------|------|
| < 2 分钟 | 3 张 | 固定点 |
| 2-5 分钟 | 5 张 | 固定点 |
| > 5 分钟 | 7 张 | 均匀分布 |

### OSS 上传策略

| 模式 | URL 类型 | 有效期 | 适用场景 |
|------|----------|--------|----------|
| 公开读 | `https://bucket.oss-region.aliyuncs.com/key` | 永久 | 图床、公开分享 |
| 私有读 | `https://bucket.oss-region.aliyuncs.com/key?OSSAccessKeyId=...&Expires=...&Signature=...` | 可配置（默认 2 小时） | 临时分享、敏感内容 |

---

## 输出格式

生成的总结包含：

1. **标题 + Tags + Status + Author** — 元数据头部
2. **📝 Note** — 100-200 字 AI 生成概述
3. **📺 视频信息** — 链接、时长、UP 主、字幕来源
4. **🎯 核心要点** — emoji + 描述 + 时间戳（AI 提取）
5. **⚠️ 注意事项** — 特别提醒（AI 提取）
6. **📚 关键概念** — 术语解释表格（AI 提取）
7. **🎬 视频帧截图** — 带时间戳的 OSS 图床链接
8. **💡 总结** — AI 生成的最终归纳

---

## 依赖

### 必需

- `yt-dlp` - 视频/字幕下载
- `ffmpeg` - 视频处理/截图/音频转换
- `python3` - 字幕分析、OSS 上传、Notion 推送
- `requests` - Python HTTP 库（Notion API）
- `oss2` - 阿里云 OSS Python SDK

### 可选（Plan B）

```bash
# 本地 Whisper（离线转录）
pip install openai-whisper

# 或使用 Groq API（在线，快速）
# 设置 WHISPER_API_KEY 环境变量
```

### 安装依赖

```bash
# 安装 Python 依赖
pip3 install requests oss2 python-dotenv

# 检查必需工具
yt-dlp --version
ffmpeg -version
python3 --version
```

---

## 故障排查

### 字幕下载失败

```bash
# 检查 Cookies 是否有效
yt-dlp --cookies ~/.cookies/bilibili_cookies.txt \
       --list-subs "URL"

# 如果提示 401，Cookies 过期，需重新导出
```

### 视频下载失败

```bash
# 检查网络连接
ping www.bilibili.com

# 检查磁盘空间
df -h /tmp

# 手动测试下载
yt-dlp -f "best[height<=720]" "URL"
```

### 截图失败

```bash
# 检查 ffmpeg 是否安装
ffmpeg -version

# 检查视频是否下载完成
ls -la video.mp4

# 验证视频文件
ffprobe -v error -show_entries format=duration video.mp4
```

### 字幕文本提取为空

```bash
# 检查字幕文件
cat video.zh-Hans.vtt

# 手动提取测试
awk '/^WEBVTT/{next} /^[0-9]/{next} /^$/{next} /-->/ {next} {print}' video.vtt
```

### OSS 上传失败

```bash
# 检查环境变量配置
cat ~/.openclaw/.env | grep ALIYUN_OSS

# 测试单文件上传
python3 ~/.openclaw/skills/video-summarizer/scripts/upload-to-oss.py \
    upload /path/to/image.jpg --public

# 检查网络连接
ping oss-cn-shanghai.aliyuncs.com
```

### Notion 推送失败

```bash
# 检查 API Key 配置
cat ~/.openclaw/.env | grep NOTION

# 测试 Database 访问
curl -X POST "https://api.notion.com/v1/data_sources/YOUR_DATABASE_ID/query" \
  -H "Authorization: Bearer YOUR_NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json"

# 检查 Database ID 是否正确
# Database ID 是 URL 中的 32 位字符串：https://www.notion.so/xxx/Database-ID-32chars
```

---

## 示例

### 完整示例（推荐流程）

```bash
cd ~/.openclaw/skills/video-summarizer

# 1. 下载 + 分析 + OSS 上传
./scripts/video-summarize-oss.sh \
    "https://www.bilibili.com/video/BV1eTPEzNEqf/" \
    /tmp/video-test \
    ~/.cookies/bilibili_cookies.txt

# 2. 查看推送预览
cat /tmp/video-test/PUSH_PREVIEW.txt

# 3. 老大审阅后，推送到 Notion
python3 scripts/push-to-notion.py \
    /tmp/video-test/summary-ai.md

# 4. 查看结果
cat /tmp/video-test/summary-ai.md

# 5. 查看 OSS 截图链接
ls -lh /tmp/video-test/screenshots/
```

### 分步示例

```bash
# Step 1: 下载视频和字幕
./scripts/video-summarize.sh \
    "https://www.bilibili.com/video/BVxxx" \
    /tmp/output \
    ~/.cookies/bilibili_cookies.txt

# Step 2: 手动上传截图到 OSS
python3 scripts/upload-to-oss.py \
    batch /tmp/output/screenshots \
    --prefix "screenshots/20260325/" \
    --public

# Step 3: AI 分析生成总结
python3 scripts/analyze-subtitles-ai.py \
    /tmp/output/video.zh-Hans.vtt \
    /tmp/output/metadata.json \
    /tmp/output/summary-ai.md

# Step 4: 推送到 Notion
python3 scripts/push-to-notion.py \
    /tmp/output/summary-ai.md
```

---

## 经验教训

### ✅ 已验证的最佳实践

1. **元数据解析用 Python** — 比 grep 更可靠
2. **字幕提取用 awk** — 避免 grep 参数问题
3. **视频下载必须重试** — 网络波动常见
4. **截图用 -update 参数** — 避免 ffmpeg 报错
5. **Cookies 定期更新** — 过期会导致字幕失败
6. **OSS 上传用时间戳前缀** — 避免文件名冲突
7. **Notion 推送前生成预览** — 让老大确认后再推送
8. **总结分基础版和 AI 版** — AI 版质量更高

### ⚠️ 已知问题

1. **B 站音频下载不稳定** — 偶发连接拒绝，重试可解决
2. **字幕需要登录** — 部分视频无自动字幕
3. **Notion API 限制** — 每次最多 100 个 blocks，长内容需分批
4. **OSS 签名 URL 有效期** — 私有 Bucket 需注意过期时间

### ✅ v2.0 已完成

1. **阿里云 OSS 图床集成** — 截图自动上传，生成永久链接
2. **Notion 推送集成** — 一键推送到 Notion Database
3. **推送预览机制** — 老大确认后再推送，避免误操作
4. **七牛云备选方案** — `upload-to-qiniu.py` 作为备用图床

### 🔜 待优化

1. **批量处理** — 一次处理多个视频（播放列表）
2. **多平台支持增强** — YouTube、抖音、小红书等
3. **AI 分析优化** — 更精准的核心要点提取
4. **Web UI** — 可视化操作界面

---

## 测试记录

### v2.0 测试 (2026-03-25)

**视频:** BV1eTPEzNEqf/ (解决 OpenClaw 长期记忆 4 种方法)  
**时长:** 11:48  
**结果:** ✅ 全部成功

| 步骤 | 状态 | 说明 |
|------|------|------|
| 元数据 | ✅ | Python 解析正确 |
| 字幕 | ✅ | Cookies 有效，19KB |
| 文本提取 | ✅ | 321 行，382 字 |
| 视频下载 | ✅ | 第 2 次重试成功 |
| 截图 | ✅ | 7/7 张全部成功 |
| OSS 上传 | ✅ | 7/7 张上传成功，生成永久链接 |
| AI 总结 | ✅ | 完整结构化文档 |
| Notion 推送 | ✅ | 页面创建成功，内容完整 |

### v1.3 测试 (2026-03-22)

**视频:** BV1eTPEzNEqf/  
**时长:** 11:48  
**结果:** ✅ 全部成功（基础流程验证）

| 步骤 | 状态 | 说明 |
|------|------|------|
| 元数据 | ✅ | Python 解析正确 |
| 字幕 | ✅ | Cookies 有效，19KB |
| 文本提取 | ✅ | 321 行，382 字 |
| 视频下载 | ✅ | 第 2 次重试成功 |
| 截图 | ✅ | 7/7 张全部成功 |
| 总结生成 | ✅ | 完整结构化文档 |

---

## 快速参考

### 常用命令

```bash
# 快速处理一个视频（完整流程）
~/.openclaw/skills/video-summarizer/scripts/video-summarize-oss.sh \
    "视频 URL" /tmp/output ~/.cookies/bilibili_cookies.txt

# 查看总结
cat /tmp/output/summary-ai.md

# 推送到 Notion
python3 ~/.openclaw/skills/video-summarizer/scripts/push-to-notion.py \
    /tmp/output/summary-ai.md

# 检查配置
cat ~/.openclaw/.env | grep -E "(ALIYUN_OSS|NOTION)"
```

### 环境变量检查清单

```bash
# 必需（OSS 图床）
ALIYUN_OSS_AK=
ALIYUN_OSS_SK=
ALIYUN_OSS_BUCKET_ID=
ALIYUN_OSS_ENDPOINT=

# 必需（Notion 推送）
NOTION_API_KEY=
NOTION_VIDEO_SUMMARY_DATABASE_ID=

# 可选
WHISPER_API_KEY=
AUTO_PUSH_TO_NOTION=false
```

---

**维护者:** secretary  
**联系方式:** 钉钉 (044463661936452286)  
**文档:** ~/.openclaw/skills/video-summarizer/SKILL.md  
**版本:** v2.0 (2026-03-25)
