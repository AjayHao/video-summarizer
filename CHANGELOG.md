# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.10] - 2026-04-14

### 🔒 安全合规优化

**移除硅基流动 API 残留代码**:
- `douyin_downloader.py` 移除硅基流动 (siliconflow.cn) API 配置和调用
- 改用与主流程一致的 Groq API + 本地 Faster-Whisper 降级方案
- 更新环境变量：`API_KEY` → `GROQ_API_KEY`（与其他脚本统一）
- 文档同步更新：SKILL.md、CHANGELOG.md 移除硅基流动相关描述

**Notion 推送说明优化**:
- `push-to-notion.py` 改进错误提示，明确说明 NOTION_API_KEY 为可选配置
- 仅在 `--push` 模式时需要配置，非强制依赖
- 添加获取 API Key 的官方链接

**外部服务端点文档更新**:
- SKILL.md 添加抖音域名到外部服务端点表格
- 明确各服务的数据传输范围和用途

### 📝 文档更新

**抖音平台说明**:
- 澄清 `douyin_downloader.py` 仅用于元数据获取和视频下载
- 语音转录使用主流程的 `transcribe-audio.py`（Groq API + 本地降级）
- 添加故障排查条目：抖音文案提取失败自动降级到本地 Faster-Whisper

**环境变量说明**:
- GROQ_API_KEY 注释说明：douyin_downloader.py 也使用此变量
- 移除所有硅基流动 API 相关的环境变量说明

---

## [1.0.9] - 2026-04-12

### 📝 文档更新

**Groq 配置说明优化**:
- 明确标注 Groq API 为**可选配置**，非强制依赖
- 更新文档说明：未配置 GROQ_API_KEY 时自动使用本地 Faster-Whisper
- 移除「硅基流动」相关描述（代码已删除）
- Plan B 降级方案从「三层」改为「双层」（Groq API → Faster-Whisper）

**Notion 配置简化**:
- 移除多数据库支持（`NOTION_VIDEO_SUMMARY_DATABASE_IDS`）
- 仅保留单数据库配置（`NOTION_VIDEO_SUMMARY_DATABASE_ID`）

### 🔧 代码优化

**版本号统一**:
- SKILL.md: 1.0.8 → 1.0.9
- README.md: 1.0.8 → 1.0.9
- video-summarize.sh: 1.0.8 → 1.0.9
- transcribe-audio.py: 1.0.8 → 1.0.9
- analyze-subtitles-ai.py: 1.0.8 → 1.0.9
- push-to-notion.py: 1.0.8 → 1.0.9
- prompt.json: 1.0.8 → 1.0.9
- upload-to-oss.py: 1.0.8 → 1.0.9

### 🐛 Bug 修复

**cover_url.txt 写入问题**:
- 修复封面上传结果追加写入导致解析失败的问题（`>>` → `>`）

---

## [1.0.8] - 2026-04-11

### 🚨 安全漏洞修复

**修复命令注入漏洞（VirusTotal 报告）**:

1. **Step 1 元数据生成（抖音平台）**
   - ❌ 修复前：heredoc 直接展开 `$TITLE` 等变量，存在命令注入风险
   - ✅ 修复后：使用 Python `json.dump()` 安全生成 JSON（自动转义特殊字符）
   - 攻击场景：视频标题包含 `"; rm -rf ~ #` 等恶意内容时可执行任意命令

2. **save_progress() 函数**
   - ❌ 修复前：heredoc 直接展开 `$VIDEO_URL` 和 `$OUTPUT_DIR`
   - ✅ 修复后：使用 Python `json.dump()` 安全生成进度文件

3. **其他 heredoc 审查**
   - `cat > "$AI_JSON_FILE" << 'AIJSON'` → ✅ 安全（带引号，变量不展开）
   - 其余 heredoc 均为静态内容或已修复

### 🎙️ 转录优化

**简化语音转录降级逻辑**:

1. **移除硅基流动 API 支持**
   - ❌ 删除 `transcribe_with_siliconflow()` 函数
   - ❌ 移除 `SILICONFLOW_API_KEY` 环境变量依赖
   - ✅ 减少 1 个 API Key 配置

2. **优化 Groq API 降级逻辑**
   - ✅ 检测 `GROQ_API_KEY` 是否存在且非空
   - ✅ Groq API 调用失败时（网络/配额）自动降级到本地
   - ✅ 未配置 Key 时直接使用本地转录

3. **三层降级方案**
   ```
   1. Groq API (whisper-large-v3) → 云端高速（如果配置且可用）
   2. Faster-Whisper (本地) → GPU/CPU 自适应
   3. Whisper.cpp / OpenAI Whisper → 保底方案
   ```

### 🔒 安全合规优化

**修复 OpenClaw 安全扫描问题（Suspicious → Benign）：**

1. **环境变量声明补全**
   - 在 metadata 中添加 `ALIYUN_OSS_ENDPOINT` 到 required env
   - 解决脚本使用但未声明的警告

2. **依赖声明补全**
   - pip packages 添加 `biliup`（B 站登录工具）
   - 解决依赖未声明的警告

3. **安全透明度增强**
   - 新增「安全提示」警告框（SKILL.md 开头）
   - 新增「安全与隐私说明」章节：
     - 敏感数据处理表格（文件/用途/敏感性/用户控制）
     - 外部服务端点列表（域名/用途/传输数据）
     - 最小权限建议（OSS Bucket/API Keys/测试环境）

**修复 OpenClaw 安全扫描问题（Suspicious → Benign）：**

1. **环境变量声明补全**
   - 在 metadata 中添加 `ALIYUN_OSS_ENDPOINT` 到 required env
   - 解决脚本使用但未声明的警告

2. **依赖声明补全**
   - pip packages 添加 `biliup`（B 站登录工具）
   - 解决依赖未声明的警告

3. **安全透明度增强**
   - 新增「安全提示」警告框（SKILL.md 开头）
   - 新增「安全与隐私说明」章节：
     - 敏感数据处理表格（文件/用途/敏感性/用户控制）
     - 外部服务端点列表（域名/用途/传输数据）
     - 最小权限建议（OSS Bucket/API Keys/测试环境）

### 📊 扫描结果对比

| 扫描项 | 优化前 | 优化后 |
|--------|--------|--------|
| 环境变量匹配 | ❌ 缺失 `ALIYUN_OSS_ENDPOINT` | ✅ 完整声明 |
| 依赖透明度 | ❌ `biliup` 未声明 | ✅ 完整列出 |
| Cookie 处理 | ⚠️ 标记为敏感 | ✅ 明确声明 + 用户可控 |
| 外部端点 | ⚠️ 未明确列出 | ✅ 透明列表 |

---

## [1.0.7] - 2026-04-07

---

## 🎯 版本概述

v1.0.7 是一个 **B 站登录与 Cookies 支持完善** 版本，专注于修复 B 站扫码登录流程和 yt-dlp Cookies 参数传递问题，确保 B 站视频处理能够绕过 412 风控限制。

**核心改进**:
- ✅ 修复 B 站扫码登录 Cookies 路径检测
- ✅ 支持 biliup 新格式 Cookie 转换
- ✅ 全链路添加 yt-dlp `--cookies` 参数
- ✅ 保留 Cookie 原始过期时间

---

## 🐛 Bug 修复

### 1. B 站扫码登录 Cookies 路径检测失败

**问题**: `biliup login` 在**当前工作目录**生成 `cookies.json`，但脚本检查的是 `~/.config/biliup/cookies.json`，路径不匹配导致检测失败。

**修复方案**:
- 修改 `bili-login.sh` 在脚本目录执行 `biliup login`
- 直接检查 `$SCRIPT_DIR/cookies.json`
- 增加预期路径提示，便于排查

**修改文件**: `scripts/bili-login.sh` (第 8-42 行)

**代码改动**:
```bash
# 修改前
BILIUP_COOKIE="$HOME/.config/biliup/cookies.json"
biliup login
if [[ ! -f "$BILIUP_COOKIE" ]]; then
    echo "❌ 登录失败"
fi

# 修改后
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BILIUP_COOKIE="$SCRIPT_DIR/cookies.json"
cd "$SCRIPT_DIR"
biliup login
if [[ ! -f "$BILIUP_COOKIE" ]]; then
    echo "❌ 登录失败，未找到 cookies.json"
    echo "   预期路径：$BILIUP_COOKIE"
    exit 1
fi
```

---

### 2. Cookie 转换不支持 biliup 新格式

**问题**: `convert-bili-cookie.py` 只支持旧格式 `{"cookie": {...}}`，不支持 biliup 新格式 `{"cookie_info": {"cookies": [...]}}`，导致转换后 0 个 Cookie。

**修复方案**:
- 支持 3 种 Cookie 格式（新格式、旧格式、兼容模式）
- 从 `cookie_info.cookies` 数组提取 Cookie
- 保留原始过期时间（`expires` 字段）

**修改文件**: `scripts/convert-bili-cookie.py` (第 17-62 行)

**代码改动**:
```python
# 修改前
cookies = data.get('cookie', {})
if not cookies:
    cookies = data

expire_time = int(time.time()) + 7776000  # 硬编码 90 天

# 修改后
cookies_dict = {}

# 格式 1: cookie_info.cookies 数组（biliup 新格式）
cookie_info = data.get('cookie_info', {})
if cookie_info and 'cookies' in cookie_info:
    for cookie in cookie_info['cookies']:
        name = cookie.get('name', '')
        value = cookie.get('value', '')
        if name and value:
            cookies_dict[name] = value

# 格式 2: cookie 对象（旧格式）
# 格式 3: 直接就是 cookie 字典（兼容模式）

# 保留原始过期时间
expires_map = {}
for cookie in cookie_info['cookies']:
    name = cookie.get('name', '')
    expires = cookie.get('expires', 0)
    if name and expires:
        expires_map[name] = expires

expire_time = expires_map.get(field, int(time.time()) + 7776000)
```

**测试验证**:
```json
// 输入：biliup 新格式
{
  "cookie_info": {
    "cookies": [
      {"name": "SESSDATA", "value": "...", "expires": 1791038234}
    ]
  }
}

// 输出：Netscape 格式
.bilibili.com	TRUE	/	TRUE	1791038234	SESSDATA	...
```

---

### 3. yt-dlp 缺少 --cookies 参数（412 风控）

**问题**: B 站视频处理时，yt-dlp 调用未传递 Cookies 参数，导致 412 风控错误。

**影响范围**:
- Step 1: 元数据获取（`--dump-json`）
- Step 2: 视频下载（`-f best`）
- Step 3: 字幕下载（`--write-auto-sub`）

**修复方案**:
- 所有 yt-dlp 调用增加 Cookies 检查
- 有 Cookies 文件时添加 `--cookies` 参数
- 无 Cookies 文件时保持原有行为（兼容）

**修改文件**: `scripts/video-summarize.sh`

#### 3.1 Step 1: 元数据获取（第 301-322 行）

```bash
# 修改前
yt-dlp --dump-json "$VIDEO_URL" > "$OUTPUT_DIR/metadata.json"

# 修改后
if [[ -f "$COOKIES_FILE" ]]; then
    yt-dlp --cookies "$COOKIES_FILE" --dump-json "$VIDEO_URL" > "$OUTPUT_DIR/metadata.json"
else
    yt-dlp --dump-json "$VIDEO_URL" > "$OUTPUT_DIR/metadata.json"
fi
```

#### 3.2 Step 2: 视频下载（第 428-462 行）

```bash
# 修改前
yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
       --merge-output-format mp4 \
       -o "$VIDEO_FILE" "$VIDEO_URL"

# 修改后
COOKIE_ARG=""
if [[ -n "$COOKIES_FILE" && -f "$COOKIES_FILE" ]]; then
    COOKIE_ARG="--cookies $COOKIES_FILE"
fi

yt-dlp $COOKIE_ARG -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
       --merge-output-format mp4 \
       -o "$VIDEO_FILE" "$VIDEO_URL"
```

#### 3.3 Step 3: 字幕下载（第 508-528 行）

```bash
# 修改前
yt-dlp --write-auto-sub \
       --sub-lang "zh-Hans,zh,en" \
       --skip-download \
       --convert-subs vtt \
       -o "$OUTPUT_DIR/video" "$VIDEO_URL"

# 修改后
SUBTITLE_COOKIE_ARG=""
if [[ -n "$COOKIES_FILE" && -f "$COOKIES_FILE" ]]; then
    SUBTITLE_COOKIE_ARG="--cookies $COOKIES_FILE"
fi

yt-dlp $SUBTITLE_COOKIE_ARG --write-auto-sub \
       --sub-lang "zh-Hans,zh,en" \
       --skip-download \
       --convert-subs vtt \
       -o "$OUTPUT_DIR/video" "$VIDEO_URL"
```

---

## 📊 变更统计

### 文件修改

| 文件 | 新增行 | 删除行 | 改动说明 |
|------|--------|--------|----------|
| `scripts/bili-login.sh` | +10 | -3 | 修复 Cookies 路径检测 |
| `scripts/convert-bili-cookie.py` | +38 | -6 | 支持 biliup 新格式 + 保留过期时间 |
| `scripts/video-summarize.sh` | +43 | -10 | 全链路添加 --cookies 参数 |
| **总计** | **+91** | **-19** | **净增 +72 行** |

### yt-dlp 调用统计

| 步骤 | 调用位置 | Cookies 支持 | 数量 |
|------|----------|-------------|------|
| **Step 1: 元数据** | 第 305-322 行 | ✅ 已添加 | 6 处 |
| **Step 2: 视频下载** | 第 440-462 行 | ✅ 已添加 | 4 处 |
| **Step 3: 字幕下载** | 第 517-528 行 | ✅ 已添加 | 2 处 |
| **总计** | - | ✅ 100% | **12 处** |

---

## 🧪 测试验证

### B 站扫码登录

```bash
cd ~/.openclaw/skills/video-summarizer/scripts
./bili-login.sh
```

**预期结果**:
```
✅ 登录成功
🔄 转换 Cookies 格式...
✅ Cookies 已保存：~/.cookies/bilibili_cookies.txt
```

### Cookie 转换

```bash
python3 convert-bili-cookie.py cookies.json ~/.cookies/bilibili_cookies.txt
```

**输入** (biliup 新格式):
```json
{
  "cookie_info": {
    "cookies": [
      {"name": "SESSDATA", "value": "...", "expires": 1791038234}
    ]
  }
}
```

**输出** (Netscape 格式):
```
✅ 转换成功 | 5 个 Cookie
.bilibili.com	TRUE	/	TRUE	1791038234	SESSDATA	...
```

### B 站视频处理

```bash
./video-summarize.sh "https://www.bilibili.com/video/BV1j1ECzjE28" /tmp/test
```

**预期结果**:
- ✅ 元数据获取成功（无 412 错误）
- ✅ 视频下载成功
- ✅ 字幕下载成功（或 Plan B 语音转录）
- ✅ AI 分析成功
- ✅ Notion 推送成功

---

## ⚠️ 兼容性说明

### 向后兼容
- ✅ 完全兼容 v1.0.6
- ✅ 无 Cookies 文件时保持原有行为
- ✅ 支持 biliup 新旧两种 Cookie 格式

### 升级步骤
```bash
cd ~/.openclaw/skills/video-summarizer
git pull origin main
```

### 依赖要求
- **biliup**: >= 1.1.29（已安装）
- **yt-dlp**: >= 2026.03.17
- **ffmpeg**: >= 6.1

---

## 🔜 后续计划

- [ ] 添加 Cookies 过期检测与自动刷新
- [ ] 支持更多视频平台（TikTok、Instagram Reels）
- [ ] 性能优化（截图并行上传、结果缓存）
- [ ] 单元测试（核心函数覆盖率 80%+）

---

## 📞 反馈与支持

- **GitHub Issues**: https://github.com/AjayHao/video-summarizer/issues
- **Gitee Issues**: https://gitee.com/ajayhao/video-summarizer/issues
- **OpenClaw Skill**: 已发布到 clawdhub
- **维护人**: Ajay Hao

---

_感谢使用 Video Summarizer！_

**生成时间**: 2026-04-07  
**版本**: v1.0.7


## [1.0.6] - 2026-04-06

### 🐛 Bug 修复

**AI 分析纯文本格式支持**:
- 修复 `analyze-subtitles-ai.py` 的 `parse_vtt()` 函数
- 增加纯文本格式检测（无 WEBVTT 头部和时间戳）
- 支持 Plan B 语音转录生成的 `audio.txt` 文件
- 用户反馈：AI 分析报错"找到 0 条字幕"

**抖音元数据 JSON 格式错误**:
- 修复 `video-summarize.sh` 中抖音标题提取
- 清理标题中的换行符和回车符
- 避免 JSON 解析失败（invalid control character）
- 用户反馈：脚本执行失败（退出码：1）

### 📊 变更统计

- 修改文件：2 个
- 新增代码：+15 行
- 删除代码：-3 行

### ✅ 核心平台（4 个）

- **Bilibili（B 站）** - 完整支持
- **YouTube** - 完整支持
- **小红书** - 基本支持（语音转录）
- **抖音** - 完整支持（专用下载器，无需 cookies）

### 🧪 测试验证

**抖音视频测试**:
- 视频：https://www.douyin.com/video/7601482272836041670
- 标题：2026 年 AI 大模型权威排名及详细解析
- ✅ 视频下载成功（17M）
- ✅ 语音转录成功（3005 字符）
- ✅ AI 分析成功（生成 JSON）
- ✅ 截图生成（11 张）
- ✅ Notion 推送成功

## [1.0.5] - 2026-04-06

### 🐛 Bug 修复

**抖音下载链接提取失败**:
- 修复 `video-summarize.sh` 中抖音下载链接提取 bug
  - 从 `cut -d' ' -f2` 改为 `sed 's/下载链接：//'`
  - 避免 URL 包含中文前缀导致 curl 失败
- 修复 `download-audio.sh` 中同样的 URL 提取 bug
- 用户反馈：专用下载器获取不到有效下载链接

### 🔧 优化改进

**移除抖音平台的 yt-dlp 依赖**:
- 抖音只使用专用下载器（`douyin_downloader.py` + `curl`）
- 移除 yt-dlp 降级逻辑（需要 cookies，防盗链限制）
- 失败时直接退出，不回退到 yt-dlp
- 非抖音平台继续使用 yt-dlp

### 📊 变更统计

- 修改文件：2 个
- 新增代码：+16 行
- 删除代码：-4 行

### ✅ 核心平台（4 个）

- **Bilibili（B 站）** - 完整支持
- **YouTube** - 完整支持
- **小红书** - 基本支持（语音转录）
- **抖音** - 完整支持（专用下载器，无需 cookies）

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
