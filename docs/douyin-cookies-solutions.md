# 抖音 Cookies 获取方案对比

## 📋 三种方案

### 方案 1：yt-dlp 浏览器读取（推荐 ⭐）

**脚本**：`douyin-login-v2.sh`

**原理**：利用 yt-dlp 的 `--cookies-from-browser` 功能，直接从已登录的浏览器读取 Cookies

**优点**：
- ✅ 最简单，无需额外工具
- ✅ 自动保存为 Netscape 格式
- ✅ 支持 Chrome/Firefox/Edge 等主流浏览器
- ✅ 浏览器登录一次，脚本随时可用

**缺点**：
- ⚠️ 需要先在浏览器中手动登录抖音
- ⚠️ Cookies 有效期约 30-90 天

**使用**：
```bash
# 自动尝试所有浏览器
./douyin-login-v2.sh auto

# 指定浏览器
./douyin-login-v2.sh chrome
./douyin-login-v2.sh firefox
./douyin-login-v2.sh edge
```

---

### 方案 2：虚拟浏览器自动登录（高级 🔧）

**脚本**：`douyin-login-auto.py`

**原理**：使用 Playwright 启动虚拟浏览器，自动打开抖音登录页，用户扫码后保存 Cookies

**优点**：
- ✅ 完全自动化流程
- ✅ 无需手动导出 Cookies
- ✅ 可视化操作，用户体验好
- ✅ 可以处理复杂的登录流程

**缺点**：
- ⚠️ 需要安装 Playwright 和浏览器（约 100MB）
- ⚠️ 首次运行较慢（需下载浏览器）
- ⚠️ 仍需用户扫码/手机号登录

**安装**：
```bash
pip3 install playwright
playwright install chromium
```

**使用**：
```bash
python3 douyin-login-auto.py
```

---

### 方案 3：手动导出（备用 💾）

**脚本**：`douyin-login.sh`（旧版）

**原理**：用户手动从浏览器导出 cookies.txt

**优点**：
- ✅ 不依赖任何工具
- ✅ 最稳定可靠

**缺点**：
- ❌ 操作繁琐
- ❌ 每次过期需重复操作

**使用**：
```bash
./douyin-login.sh
# 按提示手动复制 Cookie
```

---

## 🎯 推荐方案

| 场景 | 推荐方案 | 原因 |
|------|----------|------|
| 快速获取 | **方案 1** | 最简单，一条命令 |
| 长期稳定 | **方案 1** | 浏览器保持登录即可 |
| 自动化需求 | **方案 2** | 完全自动，体验好 |
| 无 yt-dlp | **方案 3** | 不依赖外部工具 |

---

## 🔧 集成到 video-summarize.sh

当前已实现：

```bash
# 自动选择 Cookies
if [[ "$PLATFORM" == "douyin" ]]; then
    COOKIES_FILE="$DOUYIN_COOKIES_FILE"
    if [[ ! -f "$COOKIES_FILE" ]]; then
        log_warn "抖音 Cookies 不存在"
        log_warn "请先运行：./douyin-login-v2.sh auto"
    fi
fi
```

**使用流程**：

1. **首次使用**：
   ```bash
   # 获取 Cookies（只需一次）
   ./douyin-login-v2.sh auto
   
   # 然后正常使用
   ./video-summarize.sh "https://v.douyin.com/xxx"
   ```

2. **后续使用**：
   ```bash
   # 直接使用，自动读取 Cookies
   ./video-summarize.sh "https://v.douyin.com/xxx"
   ```

3. **Cookies 过期后**：
   ```bash
   # 重新获取
   ./douyin-login-v2.sh auto
   ```

---

## 📊 技术对比

| 特性 | 方案 1 | 方案 2 | 方案 3 |
|------|--------|--------|--------|
| 依赖 | yt-dlp | Playwright | 无 |
| 安装复杂度 | ⭐ 低 | ⭐⭐ 中 | ⭐ 低 |
| 操作复杂度 | ⭐ 低 | ⭐ 低 | ⭐⭐⭐ 高 |
| 自动化程度 | ⭐⭐ 中 | ⭐⭐⭐ 高 | ⭐ 低 |
| 稳定性 | ⭐⭐⭐ 高 | ⭐⭐ 中 | ⭐⭐⭐ 高 |
| 首次耗时 | 10 秒 | 5 分钟 | 5 分钟 |
| 后续耗时 | 10 秒 | 10 秒 | 5 分钟 |

---

## ✅ 测试状态

- [x] 方案 1 脚本创建
- [x] 方案 2 脚本创建
- [x] 方案 3 脚本保留
- [x] video-summarize.sh 集成
- [ ] 实际测试验证（需要抖音账号）

---

## 📝 注意事项

1. **Cookies 有效期**：约 30-90 天，过期后需重新获取
2. **多账号支持**：不同账号的 Cookies 保存为不同文件
3. **安全性**：Cookies 文件包含登录凭证，请妥善保管
4. **隐私**：不要在公共环境保存 Cookies
