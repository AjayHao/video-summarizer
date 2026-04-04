# 抖音 Cookies 获取指南（v0.1.4）

> 📌 **核心提示**：只需 3 分钟，一次设置，30-90 天免登录！

---

## 🚀 快速开始（3 分钟）

### 前提条件

1. ✅ **已安装 yt-dlp**
   ```bash
   yt-dlp --version  # 检查版本
   ```

2. ✅ **已在浏览器登录抖音**（手机扫码，无需输入密码）
   - 打开浏览器访问：https://www.douyin.com
   - 使用抖音 APP 扫码登录
   - 确认能看到用户头像

### 一键获取 Cookies

```bash
cd ~/.openclaw/skills/video-summarizer/scripts
./douyin-login-v2.sh auto
```

**预期输出**：
```
🤖 自动模式：尝试从浏览器读取
🔍 尝试从 chrome 读取 Cookies...
✅ 从 chrome 读取 Cookies 成功

✅ Cookies 获取成功！
📁 保存位置：/home/ajayhao/.cookies/douyin_cookies.txt
```

### 立即使用

```bash
# 处理抖音视频
./video-summarize.sh "https://v.douyin.com/bQ2chgMWotA/" --verbose
```

---

## 📋 方案对比

| 方案 | 操作 | 复杂度 | 推荐度 | 适用场景 |
|------|------|--------|--------|----------|
| **方案 1：浏览器读取** | 自动读取 | ⭐ 简单 | ⭐⭐⭐ **推荐** | 有浏览器的环境 |
| **方案 2：手动导出** | 扩展导出 | ⭐⭐ 中等 | ⭐⭐ 备用 | Snap 浏览器/服务器 |
| **方案 3：Playwright** | 虚拟浏览器 | ⭐⭐⭐ 复杂 | ❌ 已弃用 | 需要 sudo 权限 |

**当前采用**：方案 1（yt-dlp 浏览器读取）

**选择理由**：
- ✅ 无需额外依赖（只需 yt-dlp）
- ✅ 无需 sudo 权限
- ✅ 支持 Chrome/Firefox/Edge
- ✅ 用户只需手机扫码（无需 PC 登录账号）
- ✅ 一次登录，Cookies 可用 30-90 天

---

## 🔧 详细操作步骤

### 方案 1：浏览器读取（推荐）

#### 适用场景
- ✅ 有图形界面的浏览器（Chrome/Firefox/Edge）
- ✅ 已在浏览器中登录抖音

#### 操作步骤

**步骤 1：自动获取 Cookies**
```bash
cd ~/.openclaw/skills/video-summarizer/scripts
./douyin-login-v2.sh auto
```

**步骤 2：指定浏览器（可选）**
```bash
# 从 Chrome 读取
./douyin-login-v2.sh chrome

# 从 Firefox 读取
./douyin-login-v2.sh firefox

# 从 Edge 读取
./douyin-login-v2.sh edge
```

**输出示例**：
```
🔍 尝试从 chrome 读取 Cookies...
✅ 从 chrome 读取 Cookies 成功
✅ Cookies 获取成功！
📁 保存位置：/home/ajayhao/.cookies/douyin_cookies.txt
```

#### 验证 Cookies

```bash
# 检查文件
ls -lh ~/.cookies/douyin_cookies.txt

# 查看内容预览
head -10 ~/.cookies/douyin_cookies.txt

# 测试有效性
yt-dlp --cookies ~/.cookies/douyin_cookies.txt \
       --simulate "https://v.douyin.com/bQ2chgMWotA/"
```

**成功标志**：显示视频信息（标题、时长等）

---

### 方案 2：手动导出（备用）

#### 适用场景
- ✅ yt-dlp 无法读取 Cookies
- ✅ Snap 版本浏览器（Ubuntu/WSL）
- ✅ 无图形界面环境（服务器）

#### 操作步骤

**步骤 1：安装浏览器扩展**

| 浏览器 | 扩展名称 | 安装链接 |
|--------|----------|----------|
| Chrome/Edge | Get cookies.txt LOCALLY | [安装](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) |
| Firefox | cookies.txt | [安装](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/) |

**步骤 2：导出 Cookies**

1. 访问 https://www.douyin.com
2. 确认已登录（手机扫码）
3. 点击扩展图标
4. 点击 "Export" 或 "导出"
5. 保存为 `douyin_cookies.txt`

**步骤 3：移动到正确位置**

```bash
# 创建目录
mkdir -p ~/.cookies

# 移动文件（假设下载到了 Downloads）
mv ~/Downloads/douyin_cookies.txt ~/.cookies/douyin_cookies.txt

# 设置权限
chmod 600 ~/.cookies/douyin_cookies.txt
```

**步骤 4：验证**

```bash
# 检查文件
ls -lh ~/.cookies/douyin_cookies.txt

# 测试 Cookies
yt-dlp --cookies ~/.cookies/douyin_cookies.txt \
       --simulate "https://v.douyin.com/bQ2chgMWotA/"
```

---

### 特殊场景处理

#### 场景 1：Snap 版本浏览器

**问题**：Snap 版 Chromium/Firefox 使用沙盒目录，yt-dlp 无法自动读取

**现象**：
```
ERROR: could not find chromium cookies database
```

**解决**：使用方案 2（手动导出）

**步骤**：
1. 安装浏览器扩展（见方案 2）
2. 手动导出 Cookies
3. 保存到 `~/.cookies/douyin_cookies.txt`

#### 场景 2：无图形界面环境（服务器）

**问题**：服务器无法打开浏览器

**解决方案 A**：在本地电脑导出后上传

```bash
# 1. 在本地电脑导出 Cookies（见方案 2）
# 2. 上传到服务器
scp douyin_cookies.txt user@server:~/.cookies/douyin_cookies.txt

# 3. 在服务器上验证
ssh user@server
yt-dlp --cookies ~/.cookies/douyin_cookies.txt \
       --simulate "https://v.douyin.com/bQ2chgMWotA/"
```

**解决方案 B**：使用远程桌面/端口转发

```bash
# 本地浏览器访问服务器上的抖音
ssh -L 8080:localhost:80 user@server
# 然后在本地浏览器访问 http://localhost:8080
```

---

## 🎬 使用 Cookies 处理视频

### 完整流程

```bash
cd ~/.openclaw/skills/video-summarizer/scripts

# 处理抖音视频
./video-summarize.sh "https://v.douyin.com/bQ2chgMWotA/" --verbose
```

### 自动执行的 9 个步骤

| 步骤 | 说明 | 输出 |
|------|------|------|
| 1️⃣ 元数据 | 获取视频信息 | `metadata.json` |
| 2️⃣ 字幕 | 下载官方字幕 | `*.vtt` |
| 3️⃣ 文本 | 提取字幕文本 | `transcript.txt` |
| 4️⃣ 视频 | 下载视频文件 | `video.mp4` |
| 5️⃣ AI 分析 | 调用 AI 分析内容 | `ai_result.json` |
| 6️⃣ 截图 | 生成关键帧截图 | `screenshots/*.jpg` |
| 7️⃣ OSS | 上传截图到图床 | `screenshot_urls.txt` |
| 8️⃣ Markdown | 渲染总结文档 | `summary.md` |
| 9️⃣ 输出 | 整理输出目录 | `/tmp/video-summarizer/douyin/xxx/` |

### 推送 Notion（可选）

```bash
python3 push-to-notion.py \
  /tmp/video-summarizer/douyin/xxx/summary.md \
  <DATABASE_ID>
```

---

## 🔄 Cookies 管理

### 查看 Cookies

```bash
# 查看文件信息
ls -lh ~/.cookies/douyin_cookies.*

# 查看内容预览
head -10 ~/.cookies/douyin_cookies.txt

# 查看完整内容
cat ~/.cookies/douyin_cookies.txt
```

### Cookies 有效期

| 属性 | 说明 |
|------|------|
| **有效期** | 约 30-90 天 |
| **过期表现** | 视频下载失败，提示需要登录 |
| **检查方法** | `yt-dlp --cookies ... --simulate "链接"` |
| **解决方法** | 重新运行 `./douyin-login-v2.sh auto` |

### 多账号管理

```bash
# 备份账号 A
cp ~/.cookies/douyin_cookies.txt ~/.cookies/douyin_accountA.txt

# 切换到账号 B
cp ~/.cookies/douyin_accountB.txt ~/.cookies/douyin_cookies.txt

# 重新获取账号 A
./douyin-login-v2.sh auto
cp ~/.cookies/douyin_cookies.txt ~/.cookies/douyin_accountA.txt
```

### 备份策略

```bash
# 创建备份目录
mkdir -p ~/.cookies/backup

# 备份当前 Cookies
cp ~/.cookies/douyin_cookies.txt \
   ~/.cookies/backup/douyin_$(date +%Y%m%d).txt

# 查看备份列表
ls -l ~/.cookies/backup/
```

---

## ⚠️ 常见问题（FAQ）

### Q1: 提示 "Cookies 不存在"

**原因**：尚未获取 Cookies

**解决**：
```bash
./douyin-login-v2.sh auto
```

---

### Q2: 提示 "从浏览器读取失败"

**可能原因**：
1. 浏览器未登录抖音
2. 浏览器未安装
3. Cookies 文件权限问题

**解决**：
```bash
# 1. 确保已在浏览器登录抖音
# 2. 检查浏览器是否安装
which chrome chromium firefox edge

# 3. 尝试手动模式
./douyin-login-v2.sh manual
```

---

### Q3: Cookies 多久过期？

**答**：约 30-90 天，具体取决于抖音的会话策略。

**检查方法**：
```bash
yt-dlp --cookies ~/.cookies/douyin_cookies.txt \
  --simulate "https://v.douyin.com/bQ2chgMWotA/"
```

如果提示需要登录，说明 Cookies 已过期。

---

### Q4: 可以在多个设备共用 Cookies 吗？

**答**：不建议。

**原因**：
- Cookies 与浏览器环境绑定
- 跨设备使用可能失效
- 不同浏览器的 Cookies 格式不同

**建议**：每个设备单独获取 Cookies。

---

### Q5: 触发反爬机制（HTTP 429）

**现象**：
```
HTTP Error 429: Too Many Requests
```

**原因**：频繁请求触发抖音限流

**解决**：
1. **等待**：12-24 小时后自动解除
2. **换账号**：使用其他抖音账号
3. **降频**：减少请求频率（建议间隔 >5 分钟）

**预防**：
- 避免短时间内多次获取 Cookies
- 使用抖音小号（降低影响）

---

### Q6: yt-dlp 提示需要 Fresh Cookies

**现象**：
```
ERROR: Fresh cookies (not necessarily logged in) are needed
```

**原因**：Cookies 已过期或失效

**解决**：
1. 重新登录抖音（刷新页面）
2. 重新导出 Cookies
3. 清理浏览器缓存后重试

---

### Q7: Snap 浏览器无法读取

**现象**：
```
ERROR: could not find chromium cookies database
```

**原因**：Snap 使用沙盒目录结构

**解决**：使用方案 2（手动导出）

**步骤**：
1. 安装浏览器扩展
2. 手动导出 Cookies
3. 保存到 `~/.cookies/douyin_cookies.txt`

---

## 📊 完整流程图

```
┌─────────────────────────────────────┐
│  1. 手机扫码登录网页版抖音          │
│     https://www.douyin.com          │
│     （只需一次，后续自动登录）      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  2. 获取 Cookies（一次性，3 分钟）  │
│     ./douyin-login-v2.sh auto       │
│     → 自动读取浏览器 Cookies        │
│     → 保存到 ~/.cookies/            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  3. 处理抖音视频（重复使用）        │
│     video-summarize.sh "链接"       │
│     → 自动读取 Cookies              │
│     → 下载 + 转录 + AI 分析          │
│     → 生成总结文档                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  4. Cookies 过期（30-90 天后）       │
│     重新执行步骤 1-2                │
└─────────────────────────────────────┘
```

---

## 🎯 最佳实践

### 1. 使用常用浏览器

**推荐**：使用你经常使用的浏览器登录抖音

**原因**：
- 浏览器保持登录状态
- Cookies 自动更新
- 更稳定可靠

### 2. 定期更新 Cookies

**建议**：每 2 个月重新获取一次

**方法**：
```bash
# 设置日历提醒
# 每 2 个月执行一次
./douyin-login-v2.sh auto
```

### 3. 备份 Cookies

```bash
# 创建备份目录
mkdir -p ~/.cookies/backup

# 每次获取后备份
cp ~/.cookies/douyin_cookies.txt \
   ~/.cookies/backup/douyin_$(date +%Y%m%d).txt
```

### 4. 隐私保护

- ✅ **使用抖音小号**：避免主账号风险
- ✅ **不要公开 Cookies**：包含登录凭证
- ✅ **定期清理**：删除过期的备份
- ✅ **设置权限**：`chmod 600 ~/.cookies/douyin_cookies.txt`

### 5. 错误处理

**遇到问题时的检查顺序**：
1. 检查 Cookies 文件是否存在
2. 测试 Cookies 是否有效
3. 查看 yt-dlp 版本是否最新
4. 检查网络连接
5. 等待反爬解除（如触发限流）

---

## 📚 相关文档

- [测试计划](douyin-test-plan.md) - 详细测试用例
- [实现总结](douyin-v0.1.4-summary.md) - 技术实现细节

---

## ✅ 快速检查清单

使用前请确认：

- [ ] 已安装 yt-dlp（`yt-dlp --version`）
- [ ] 已在浏览器登录抖音（手机扫码）
- [ ] 已运行 `./douyin-login-v2.sh auto`
- [ ] Cookies 文件已创建（`~/.cookies/douyin_cookies.txt`）
- [ ] 已验证 Cookies 有效

处理视频时确认：

- [ ] 使用正确的视频链接
- [ ] 添加 `--verbose` 查看详细日志
- [ ] 检查输出目录（`/tmp/video-summarizer/douyin/xxx/`）
- [ ] 验证生成的文件（summary.md、screenshots/）

---

## 📞 获取帮助

**遇到问题？**

1. 查看本文档的"常见问题"部分
2. 检查 `~/.cookies/douyin_cookies.txt` 是否存在
3. 运行 `./douyin-login-v2.sh auto` 重新获取
4. 查看测试计划文档了解预期行为

---

**文档版本**：v0.1.4  
**最后更新**：2026-04-04  
**维护者**：Ajay Hao
