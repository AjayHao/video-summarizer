# 抖音登录实现状态

## 📊 实现方案对比

### 方案 1：yt-dlp 浏览器读取 ⭐ 推荐

**脚本**：`douyin-login-v2.sh`

**状态**：✅ **可用**

**优点**：
- ✅ 无需额外依赖
- ✅ 直接读取已登录浏览器的 Cookies
- ✅ 一条命令完成

**缺点**：
- ⚠️ 需要用户在浏览器中手动登录抖音

**使用**：
```bash
./douyin-login-v2.sh auto
```

---

### 方案 2：Playwright 虚拟浏览器 🔧 受限

**脚本**：`douyin-login-auto.py`

**状态**：⚠️ **需要系统依赖（sudo 权限）**

**问题**：
- ❌ Chromium 需要系统库（libnspr4 等）
- ❌ 安装需要 sudo 权限
- ❌ 在无 root 权限环境无法使用

**依赖**：
```bash
# 需要安装（需要 sudo）
sudo apt-get install -y libnspr4 libnss3 libatk1.0-0 ...
# 或
playwright install-deps chromium
```

**适用场景**：
- ✅ 有 sudo 权限的服务器/个人电脑
- ❌ 受限环境（如容器、共享主机）

---

### 方案 3：手动导出 💾 备用

**脚本**：`douyin-login.sh`

**状态**：✅ **可用**

**优点**：
- ✅ 不依赖任何工具
- ✅ 最稳定

**缺点**：
- ❌ 操作繁琐

---

## ✅ 推荐方案

**⭐ 方案 1（yt-dlp 浏览器读取）** - **默认推荐**

**优势**：
- ✅ 无需额外依赖（只需 yt-dlp）
- ✅ 无需 sudo 权限
- ✅ 支持 Chrome/Firefox/Edge
- ✅ 用户只需手机扫码登录（无需 PC 登录账号）
- ✅ 一次登录，Cookies 可用 30-90 天

**使用**：
```bash
./douyin-login-v2.sh auto
```

**详细指南**：[douyin-login-guide.md](douyin-login-guide.md)

---

## 📝 方案 1 使用指南

### 前提条件

用户已在浏览器中登录抖音：
1. 打开 Chrome/Firefox/Edge
2. 访问 https://www.douyin.com
3. 扫码或手机号登录

### 获取 Cookies

```bash
cd ~/.openclaw/skills/video-summarizer/scripts
./douyin-login-v2.sh auto
```

**输出示例**：
```
🔍 尝试从 chrome 读取 Cookies...
✅ 从 chrome 读取 Cookies 成功

✅ Cookies 获取成功！
📁 保存位置：/home/ajayhao/.cookies/douyin_cookies.txt
```

### 使用 Cookies

```bash
~/.openclaw/skills/video-summarizer/scripts/video-summarize.sh \
  "https://v.douyin.com/bQ2chgMWotA/"
```

---

## 🔧 方案 2 安装指南（有 sudo 权限）

如果环境有 sudo 权限，可安装 Playwright 依赖：

```bash
# 1. 安装系统依赖
sudo playwright install-deps chromium

# 2. 验证安装
python3 douyin-login-auto.py
```

---

## 📋 决策树

```
需要抖音登录
    │
    ├─ 有 sudo 权限？
    │   ├─ 是 → 方案 2（Playwright 虚拟浏览器）
    │   └─ 否 → 方案 1（yt-dlp 浏览器读取）
    │
    ├─ 浏览器已登录抖音？
    │   ├─ 是 → 方案 1（最简单）
    │   └─ 否 → 先在浏览器登录，再用方案 1
    │
    └─ 都不满足？
        └─ 方案 3（手动导出）
```

---

## ✅ 当前可用方案

**环境**：WSL2 / 无 sudo 权限

**可用**：
- ✅ 方案 1：`douyin-login-v2.sh`
- ✅ 方案 3：`douyin-login.sh`

**不可用**：
- ❌ 方案 2：`douyin-login-auto.py`（缺少系统库）

---

## 📝 结论

1. **方案 1（yt-dlp）** 是最灵活的选择
   - 不依赖特定浏览器
   - 不需要 sudo 权限
   - 支持 Chrome/Firefox/Edge

2. **方案 2（Playwright）** 适合有 sudo 权限的环境
   - 完全自动化
   - 但依赖系统库

3. **用户选择权**
   - 用户可以自由选择在哪个浏览器登录
   - 不需要在 PC 浏览器登录抖音（用手机 APP 扫码即可）
   - 登录一次，Cookies 可用 30-90 天
