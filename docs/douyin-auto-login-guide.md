# 抖音自动登录使用指南（方案 2）

## 🎯 为什么选择方案 2？

**方案 2（虚拟浏览器自动登录）** vs **方案 1（浏览器 Cookies 读取）**

| 特性 | 方案 1 | 方案 2 |
|------|--------|--------|
| 需要在 PC 登录抖音 | ❌ 是 | ✅ 否（只需扫码） |
| 依赖本地浏览器 | ✅ 是 | ❌ 否（独立浏览器） |
| 隐私保护 | ⚠️ 一般 | ✅ 好（独立环境） |
| 适用场景 | PC 已登录 | 任何场景 |

**方案 2 优势**：
- ✅ 不需要在 PC 浏览器登录抖音
- ✅ 使用独立虚拟浏览器，不依赖本地 Chrome/Firefox
- ✅ 扫码登录，保护隐私
- ✅ 自动化程度高

---

## 📦 安装（一次性）

### Step 1: 安装 Playwright

```bash
pip3 install playwright --break-system-packages
```

### Step 2: 安装 Chromium 浏览器

```bash
playwright install chromium
```

**下载大小**：约 110MB  
**安装位置**：`~/.cache/ms-playwright/chromium_headless_shell-1208`

### Step 3: 验证安装

```bash
cd ~/.openclaw/skills/video-summarizer/scripts
python3 test-douyin-login.py
```

**预期输出**：
```
✅ Playwright 已安装
✅ Chromium 已安装
✅ 环境检查通过！
```

---

## 🚀 使用方式

### 首次获取 Cookies

```bash
cd ~/.openclaw/skills/video-summarizer/scripts
python3 douyin-login-auto.py
```

**操作流程**：

1. **脚本启动虚拟浏览器**
   - 自动打开抖音登录页
   - 显示二维码

2. **使用抖音 APP 扫码**
   - 打开抖音 APP
   - 点击右上角搜索图标
   - 点击扫码图标 📷
   - 扫描屏幕上的二维码

3. **等待登录成功**
   - 脚本自动检测登录状态
   - 检测到用户头像后自动保存 Cookies

4. **Cookies 自动保存**
   - JSON 格式：`~/.cookies/douyin_cookies.json`
   - Netscape 格式：`~/.cookies/douyin_cookies.txt`

---

### 后续使用

Cookies 获取后，可直接使用视频总结脚本：

```bash
~/.openclaw/skills/video-summarizer/scripts/video-summarize.sh \
  "https://v.douyin.com/bQ2chgMWotA/"
```

脚本会自动：
- 识别抖音平台
- 读取 `~/.cookies/douyin_cookies.txt`
- 下载视频并处理

---

## 🔧 Cookies 管理

### 查看 Cookies

```bash
# 查看文件信息
ls -lh ~/.cookies/douyin_cookies.*

# 查看内容（JSON 格式）
cat ~/.cookies/douyin_cookies.json | head -20

# 查看内容（Netscape 格式）
cat ~/.cookies/douyin_cookies.txt | head -10
```

### Cookies 有效期

- **有效期**：约 30-90 天
- **过期表现**：视频下载失败，提示需要登录
- **解决方法**：重新运行 `python3 douyin-login-auto.py`

### 多账号支持

如需切换账号，可备份不同账号的 Cookies：

```bash
# 备份账号 A
cp ~/.cookies/douyin_cookies.txt ~/.cookies/douyin_accountA.txt

# 切换账号 B
cp ~/.cookies/douyin_accountB.txt ~/.cookies/douyin_cookies.txt
```

---

## ⚠️ 注意事项

### 1. 环境要求

- **Python**: 3.8+
- **Playwright**: 1.58.0+
- **磁盘空间**: 约 150MB（浏览器 + 依赖）

### 2. 网络要求

- 需要能访问 `https://www.douyin.com`
- 部分地区可能需要代理

### 3. 安全性

- Cookies 文件包含登录凭证，请妥善保管
- 不要将 Cookies 文件上传到公开仓库
- 建议使用独立的抖音小号

### 4. 故障排查

**问题 1：浏览器无法启动**

```bash
# 重新安装 Chromium
playwright install chromium --force
```

**问题 2：扫码后未检测到登录**

- 等待时间可能不够，脚本会等待最多 3 分钟
- 检查抖音 APP 是否已完成登录确认
- 手动按回车键继续

**问题 3：Cookies 过期**

```bash
# 重新获取
python3 douyin-login-auto.py
```

---

## 📊 使用流程

```
┌─────────────────────────────────────┐
│  1. 安装环境（一次性）              │
│     pip3 install playwright         │
│     playwright install chromium     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  2. 获取 Cookies（首次使用）        │
│     python3 douyin-login-auto.py    │
│     → 扫码登录                      │
│     → 自动保存                      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  3. 处理抖音视频（重复使用）        │
│     video-summarize.sh "链接"       │
│     → 自动读取 Cookies              │
│     → 下载 + 转录 + AI 分析          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  4. Cookies 过期（30-90 天后）       │
│     重新执行步骤 2                  │
└─────────────────────────────────────┘
```

---

## 🎯 下一步

获取 Cookies 后，测试抖音视频处理：

```bash
# 测试链接
~/.openclaw/skills/video-summarizer/scripts/video-summarize.sh \
  "https://v.douyin.com/bQ2chgMWotA/" \
  --verbose
```

**检查项**：
- [ ] 视频下载成功
- [ ] 语音转录完成
- [ ] AI 分析正常
- [ ] 截图生成并上传
- [ ] Markdown 渲染完成
- [ ] Notion 推送成功

---

## 📚 相关文档

- [方案对比](douyin-cookies-solutions.md)
- [测试计划](douyin-test-plan.md)
- [v0.1.4 计划](../CHANGELOG.md)
