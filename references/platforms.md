# 平台支持详情

> 本文档为 [SKILL.md](../SKILL.md) 的补充参考，记录四个平台的详细支持情况。

---

## Bilibili（完整支持）

**字幕**: ✅ 官方字幕 + 自动字幕  
**语音转录**: ✅ 支持（Plan B）  
**Cookies**: 推荐（获取官方字幕）  
**下载工具**: yt-dlp (>=2026.03.17)

### 操作步骤

```bash
# 1. 扫码登录（首次使用，获取官方字幕）
cd scripts
./bili-login.sh

# 2. 处理视频
./video-summarize.sh "https://www.bilibili.com/video/BV1xxxx"

# 3. 查看结果
cat /tmp/video-summarizer-*/summary.md
```

**说明**:
- Cookies 文件：`~/.cookies/bilibili_cookies.txt`
- 无 Cookies 时使用 Plan B 语音转录
- 支持 b23.tv 短链

---

## YouTube（完整支持）

**字幕**: ✅ 自动字幕（多语言）  
**语音转录**: ✅ 支持（Plan B）  
**Cookies**: ❌ 不需要  
**下载工具**: yt-dlp (>=2026.03.17)

### 操作步骤

```bash
# 直接处理（无需登录）
./video-summarize.sh "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 指定输出目录
./video-summarize.sh "https://youtu.be/dQw4w9WgXcQ" /tmp/output
```

**说明**:
- 需网络可达（可能需要代理）
- 优先下载英文字幕，无则用语音转录
- 支持 youtu.be 短链

---

## 小红书（基本支持）

**字幕**: ❌ 无字幕  
**语音转录**: ✅ 唯一方式（Plan B）  
**Cookies**: ❌ 不需要  
**下载工具**: yt-dlp (>=2026.03.17)

### 操作步骤

```bash
# 直接处理（自动使用 Plan B 语音转录）
./video-summarize.sh "https://www.xiaohongshu.com/explore/xxxx"

# 或短链
./video-summarize.sh "https://xhslink.com/o/xxxx"
```

**说明**:
- 必须使用 Plan B 语音转录
- 推荐配置 GROQ_API_KEY 加速转录
- 自动上传封面图到 OSS

---

## 抖音（完整支持）

**字幕**: ❌ 无字幕  
**语音转录**: ✅ 唯一方式（Plan B）  
**Cookies**: ❌ 不需要（专用下载器）  
**下载工具**: douyin_downloader.py

### 操作步骤

```bash
# 直接处理（专用下载器，无需 Cookies）
./video-summarize.sh "https://www.douyin.com/video/7234567890"

# 支持短链
./video-summarize.sh "https://v.douyin.com/abc123/"
```

**说明**:
- 使用专用下载器 `douyin_downloader.py`（仅用于获取元数据和下载视频）
- 无反爬限制，无需 Cookies
- 语音转录使用主流程的 `transcribe-audio.py`

---

## Plan A vs Plan B

### 对比表

| 项目 | Plan A | Plan B |
|------|--------|--------|
| **字幕来源** | 平台官方字幕 | 语音转录 |
| **准确率** | 90%+ | 80-90% |
| **速度** | 快 (1-2 分钟) | 较慢 (3-5 分钟) |
| **依赖** | Cookies（B 站） | GPU 或 API Key |

### 各平台使用情况

| 平台 | Plan A | Plan B | 默认 |
|------|--------|--------|------|
| **Bilibili** | ✅ 官方 + 自动 | ✅ 备用 | Plan A |
| **YouTube** | ✅ 自动字幕 | ✅ 备用 | Plan A |
| **小红书** | ❌ 无 | ✅ 唯一 | Plan B |
| **抖音** | ❌ 无 | ✅ 唯一 | Plan B |

### Plan B 三层降级方案

```
1. Groq API (whisper-large-v3) → 云端高速（可选，需配置 GROQ_API_KEY 且网络可达）
   └─ 失败/未配置 → 降级到本地

2. Faster-Whisper (本地) → GPU/CPU 自适应
   ├─ GPU ≥8GB  → large-v2 模型
   ├─ GPU ≥4GB  → medium 模型
   ├─ GPU ≥2GB  → small 模型
   ├─ GPU ≥1GB  → base 模型 (GPU)
   └─ 无 GPU    → base 模型 (CPU)
   └─ 失败 → 降级到方案 3

3. Whisper.cpp / OpenAI Whisper (本地保底)
   └─ 完全离线，作为最终兜底
```

**说明**: 
- Groq API 为可选配置，未配置时直接使用本地 Faster-Whisper
- 本地转录无需任何 API Key，完全离线运行
- 国内使用 Groq 需配置代理
- 抖音专用下载器也使用 Groq API + 本地降级方案
