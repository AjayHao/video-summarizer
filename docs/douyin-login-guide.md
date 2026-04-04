# 抖音 Cookies 获取指南（方案 1 - 推荐）

## 🎯 为什么选择方案 1？

**方案 1：yt-dlp 浏览器读取** 是目前最灵活、最简单的方案。

### 优势对比

| 特性 | 方案 1 | 方案 2（Playwright） |
|------|--------|----------------------|
| 依赖 | ✅ 仅 yt-dlp | ❌ 需要系统库（sudo） |
| 安装复杂度 | ⭐ 简单 | ⭐⭐⭐ 复杂 |
| 需要 PC 登录 | ❌ 否（手机扫码即可） | ❌ 否 |
| 适用环境 | ✅ 所有环境 | ⚠️ 需 sudo 权限 |
| 维护成本 | ⭐ 低 | ⭐⭐ 中 |

---

## 📦 前提条件

### 1. 已安装 yt-dlp

```bash
# 检查是否安装
yt-dlp --version

# 如未安装
pip3 install yt-dlp --break-system-packages
```

### 2. 已在浏览器中登录抖音

**重要**：不需要在 PC 上输入账号密码，只需**手机扫码登录**即可！

**操作步骤**：
1. 打开浏览器（Chrome/Firefox/Edge 等）
2. 访问 https://www.douyin.com
3. 使用抖音 APP 扫码登录
4. 确认登录成功（能看到用户头像）

---

## 🚀 获取 Cookies（一次性操作）

### 方式 1：自动模式（推荐）

```bash
cd ~/.openclaw/skills/video-summarizer/scripts
./douyin-login-v2.sh auto
```

**输出示例**：
```
🤖 自动模式：尝试从浏览器读取
🔍 尝试从 chrome 读取 Cookies...
✅ 从 chrome 读取 Cookies 成功

✅ Cookies 获取成功！
📁 保存位置：/home/ajayhao/.cookies/douyin_cookies.txt
```

### 方式 2：指定浏览器

```bash
# 从 Chrome 读取
./douyin-login-v2.sh chrome

# 从 Firefox 读取
./douyin-login-v2.sh firefox

# 从 Edge 读取
./douyin-login-v2.sh edge
```

### 方式 3：手动导出（备用）

```bash
./douyin-login-v2.sh manual
```

按提示手动导出 Cookies 并保存到 `~/.cookies/douyin_cookies.txt`

---

## 🎬 使用 Cookies 处理视频

Cookies 获取后，可直接使用视频总结脚本：

```bash
~/.openclaw/skills/video-summarizer/scripts/video-summarize.sh \
  "https://v.douyin.com/bQ2chgMWotA/" \
  --verbose
```

**脚本会自动**：
1. ✅ 识别抖音平台
2. ✅ 读取 `~/.cookies/douyin_cookies.txt`
3. ✅ 下载视频
4. ✅ 语音转录（Plan B）
5. ✅ AI 分析
6. ✅ 生成截图
7. ✅ 上传 OSS
8. ✅ 渲染 Markdown
9. ✅ 可推送 Notion

---

## 🔄 Cookies 管理

### 查看 Cookies

```bash
# 查看文件信息
ls -lh ~/.cookies/douyin_cookies.*

# 查看内容预览
head -10 ~/.cookies/douyin_cookies.txt
```

### Cookies 有效期

- **有效期**：约 30-90 天
- **过期表现**：视频下载失败，提示需要登录
- **解决方法**：重新运行 `./douyin-login-v2.sh auto`

### 多账号管理

```bash
# 备份账号 A
cp ~/.cookies/douyin_cookies.txt ~/.cookies/douyin_accountA.txt

# 切换账号 B
cp ~/.cookies/douyin_accountB.txt ~/.cookies/douyin_cookies.txt

# 重新获取账号 A
./douyin-login-v2.sh auto
cp ~/.cookies/douyin_cookies.txt ~/.cookies/douyin_accountA.txt
```

---

## ⚠️ 常见问题

### Q1: 提示 "Cookies 不存在"

**原因**：尚未获取 Cookies

**解决**：
```bash
./douyin-login-v2.sh auto
```

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

### Q3: Cookies 多久过期？

**答**：约 30-90 天，具体取决于抖音的会话策略。

**检查方法**：
```bash
# 测试视频下载
yt-dlp --cookies ~/.cookies/douyin_cookies.txt \
  --simulate "https://v.douyin.com/bQ2chgMWotA/"

# 如果提示需要登录，说明 Cookies 已过期
```

### Q4: 可以在多个设备共用 Cookies 吗？

**答**：不建议。Cookies 与浏览器环境绑定，跨设备使用可能失效。

---

## 📊 完整流程

```
┌─────────────────────────────────────┐
│  1. 手机扫码登录网页版抖音          │
│     https://www.douyin.com          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  2. 获取 Cookies（一次性）          │
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

推荐使用你经常使用的浏览器登录抖音，这样 Cookies 更稳定。

### 2. 定期更新 Cookies

建议每 2 个月重新获取一次 Cookies，避免过期影响使用。

### 3. 备份 Cookies

```bash
# 创建备份目录
mkdir -p ~/.cookies/backup

# 备份当前 Cookies
cp ~/.cookies/douyin_cookies.txt ~/.cookies/backup/douyin_$(date +%Y%m%d).txt
```

### 4. 隐私保护

- ✅ 使用抖音小号登录
- ✅ 不要在公共环境保存 Cookies
- ✅ 定期清理过期的 Cookies

---

## 📚 相关文档

- [方案对比](douyin-cookies-solutions.md)
- [测试计划](douyin-test-plan.md)
- [实现状态](douyin-login-status.md)

---

## ✅ 快速检查清单

- [ ] 已安装 yt-dlp
- [ ] 已在浏览器登录抖音（手机扫码）
- [ ] 已运行 `./douyin-login-v2.sh auto`
- [ ] Cookies 文件已创建（`~/.cookies/douyin_cookies.txt`）
- [ ] 可正常处理抖音视频

---

**最后更新**：2026-04-04  
**版本**：v0.1.4
