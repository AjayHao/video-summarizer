# 抖音支持测试计划 - v0.1.4

## 📋 测试目标

验证抖音短视频的完整处理流程，确保 v0.1.4 可以正式发布。

---

## 🔍 代码审计结果

### ✅ 已支持功能

| 模块 | 状态 | 说明 |
|------|------|------|
| 平台识别 | ✅ | `video-summarize.sh` 支持抖音 URL 识别 |
| 视频 ID 提取 | ✅ | 支持常规链接和短链 |
| 音频下载 | ✅ | `download-audio.sh` 使用 `best` 格式 |
| OSS 上传 | ✅ | `upload-to-oss.py` 有抖音识别规则 |
| 来源识别 | ✅ | `analyze-subtitles-ai.py` 识别抖音 |
| Notion 推送 | ✅ | `push-to-notion.py` 识别抖音 |

### ⚠️ 待解决问题

| 问题 | 影响 | 解决方案 |
|------|------|----------|
| **需要 Cookies** | 🔴 高 | 已创建 `douyin-login.sh` |
| **未实际测试** | 🔴 高 | 需要真实视频测试 |
| **短链支持** | 🟡 中 | yt-dlp 自动处理重定向 |

---

## 📝 测试步骤

### Step 1: 获取抖音 Cookies

```bash
# 运行登录脚本
~/.openclaw/skills/video-summarizer/scripts/douyin-login.sh
```

**操作指南**：
1. 打开浏览器访问 https://www.douyin.com
2. 登录账号（扫码或手机号）
3. 按 F12 打开开发者工具
4. 复制 Cookie 值或使用浏览器扩展导出
5. 保存到 `~/.cookies/douyin_cookies.txt`

---

### Step 2: 测试视频下载

**测试链接**：https://v.douyin.com/bQ2chgMWotA/

```bash
# 测试元数据获取
yt-dlp --dump-json "https://v.douyin.com/bQ2chgMWotA/" \
  --cookies ~/.cookies/douyin_cookies.txt

# 预期输出：JSON 格式元数据（标题、时长、封面等）
```

**检查项**：
- [ ] 成功获取元数据
- [ ] 标题正确
- [ ] 时长正确
- [ ] 封面 URL 有效

---

### Step 3: 测试完整流程

```bash
# 运行完整处理流程
~/.openclaw/skills/video-summarizer/scripts/video-summarize.sh \
  "https://v.douyin.com/bQ2chgMWotA/" \
  --verbose
```

**检查项**：
- [ ] Step 1: 元数据获取 ✅
- [ ] Step 2: 字幕下载（Plan B 语音转录）✅
- [ ] Step 3: 文本提取 ✅
- [ ] Step 4: 视频下载 ✅
- [ ] Step 5: AI 分析 ✅
- [ ] Step 6: 截图生成 ✅
- [ ] Step 7: OSS 上传（含封面）✅
- [ ] Step 8: Markdown 渲染 ✅
- [ ] Step 9: 整理输出 ✅

---

### Step 4: 验证输出

**输出目录**：`/tmp/video-summarizer/douyin/<视频 ID>`

**检查文件**：
- [ ] `metadata.json` - 元数据完整
- [ ] `audio.vtt` - 字幕文件
- [ ] `ai_result.json` - AI 分析结果
- [ ] `summary.md` - 完整总结
- [ ] `screenshots/` - 截图目录
- [ ] `screenshot_urls.txt` - OSS 链接
- [ ] `cover_url.txt` - 封面 OSS 链接

**验证内容**：
- [ ] 作者字段正确（非 Unknown）
- [ ] 时长格式正确（MM:SS）
- [ ] 封面图 OSS URL 有效
- [ ] 截图 OSS URL 有效
- [ ] Markdown 渲染正常

---

### Step 5: 测试 Notion 推送

```bash
python3 ~/.openclaw/skills/video-summarizer/scripts/push-to-notion.py \
  /tmp/video-summarizer/douyin/<视频 ID>/summary.md \
  <DATABASE_ID>
```

**检查项**：
- [ ] Notion 页面创建成功
- [ ] 封面图正常显示
- [ ] 截图正常显示
- [ ] 内容格式正确

---

## 🎯 测试用例

| 编号 | 链接类型 | 时长 | 字幕 | 预期结果 |
|------|----------|------|------|----------|
| TC1 | 短链 `v.douyin.com` | 15 秒 | 无 | Plan B 转录 |
| TC2 | 常规 `douyin.com/video` | 1 分钟 | 有 | 官方字幕 |
| TC3 | 分享链 `iesdouyin.com` | 5 分钟 | 无 | Plan B 转录 |

---

## ⏱️ 时间估算

| 步骤 | 预计时间 |
|------|----------|
| 获取 Cookies | 10 分钟 |
| Step 2-3: 下载测试 | 20 分钟 |
| Step 4-5: 验证输出 | 15 分钟 |
| 问题修复 | 30 分钟 |
| **总计** | **约 1.5 小时** |

---

## 📊 成功标准

v0.1.4 发布条件：
- [ ] 至少 1 个抖音视频完整处理成功
- [ ] 封面图上传成功
- [ ] Notion 推送成功
- [ ] 无严重 Bug
- [ ] 文档更新完成

---

## 🐛 已知问题

1. **Cookies 有效期**：约 30-90 天，过期需重新获取
2. **网络限制**：部分地区可能需要代理
3. **视频格式**：部分特殊格式可能无法下载

---

## 📝 测试记录

### 测试 1：https://v.douyin.com/bQ2chgMWotA/

**时间**：2026-04-04  
**状态**：⏳ 待测试  
**结果**：待填写

---

## 🔗 相关文档

- [抖音登录脚本](scripts/douyin-login.sh)
- [v0.1.4 计划](../CHANGELOG.md)
- [平台支持状态](../README.md)
