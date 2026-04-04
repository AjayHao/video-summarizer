# 抖音 Cookies 手动获取指南

## 📱 场景说明

当系统没有安装图形浏览器时，使用此方法。

**适用情况**：
- ✅ 服务器环境（无图形界面）
- ✅ 未安装 Chrome/Firefox 浏览器
- ✅ 使用远程桌面或 SSH 连接

---

## 🔧 准备工作

### 方式 1：使用手机扫码 + 浏览器扩展（推荐）

**步骤**：

1. **在另一台有浏览器的电脑上操作**
   - 打开 Chrome/Edge/Firefox
   - 访问 https://www.douyin.com
   - 使用抖音 APP 扫码登录

2. **安装浏览器扩展**
   
   **Chrome/Edge**：
   - 扩展名称：Get cookies.txt LOCALLY
   - 安装链接：https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
   
   **Firefox**：
   - 扩展名称：cookies.txt
   - 安装链接：https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/

3. **导出 Cookies**
   - 点击扩展图标
   - 选择"Export"或"导出"
   - 保存为 `douyin_cookies.txt`

4. **复制到目标机器**
   ```bash
   # 方式 1：scp 传输
   scp douyin_cookies.txt user@server:~/.cookies/douyin_cookies.txt
   
   # 方式 2：手动复制内容
   cat douyin_cookies.txt
   # 复制输出内容，粘贴到目标机器
   ```

---

### 方式 2：使用 yt-dlp 从其他机器读取

如果在另一台机器上有浏览器已登录：

```bash
# 在另一台机器上执行
yt-dlp --cookies-from-browser chrome \
       --cookies ~/.cookies/douyin_cookies.txt \
       --simulate "https://www.douyin.com"
```

然后复制 `~/.cookies/douyin_cookies.txt` 到目标机器。

---

### 方式 3：手动复制 Cookies（技术向）

**步骤**：

1. **在浏览器中登录抖音**
   - 访问 https://www.douyin.com
   - 扫码登录

2. **打开开发者工具**
   - 按 F12（或右键 → 检查）
   - 切换到 **Application**（应用）标签

3. **查看 Cookies**
   - 左侧：**Cookies** → **https://www.douyin.com**
   - 右侧显示所有 Cookies

4. **复制 Cookies**
   - 选中所有 Cookies（Ctrl+A）
   - 右键 → 复制（Copy）
   - 或使用扩展导出

5. **保存为 Netscape 格式**

   创建文件 `~/.cookies/douyin_cookies.txt`，内容格式：
   ```
   # Netscape HTTP Cookie File
   # https://curl.haxx.se/docs/http-cookies.html
   
   .douyin.com	TRUE	/	TRUE	1712345678	__tea_cache_tokens_	xxx
   .douyin.com	TRUE	/	TRUE	1712345678	ttwid	xxx
   ...
   ```

---

## 📝 验证 Cookies

获取 Cookies 后，验证是否有效：

```bash
# 测试 Cookies
yt-dlp --cookies ~/.cookies/douyin_cookies.txt \
       --simulate \
       "https://v.douyin.com/bQ2chgMWotA/"

# 如果成功，会显示视频信息
# 如果失败，提示需要重新获取
```

---

## 🚀 使用 Cookies

Cookies 验证通过后，可直接使用：

```bash
cd ~/.openclaw/skills/video-summarizer/scripts

# 处理抖音视频
./video-summarize.sh "https://v.douyin.com/bQ2chgMWotA/"
```

---

## ⚠️ 注意事项

### 1. Cookies 有效期

- **有效期**：约 30-90 天
- **过期表现**：视频下载失败
- **解决**：重新获取

### 2. 文件格式

确保是 **Netscape 格式**：
- 每行一个 Cookie
- 制表符分隔（不是空格）
- 包含必要的字段

### 3. 文件权限

```bash
# 设置正确的权限
chmod 600 ~/.cookies/douyin_cookies.txt
```

### 4. 文件位置

```bash
# 确保目录存在
mkdir -p ~/.cookies

# 保存位置
~/.cookies/douyin_cookies.txt
```

---

## 🔍 故障排查

### 问题 1：yt-dlp 提示 "No cookies found"

**原因**：Cookies 文件格式错误或路径不对

**解决**：
```bash
# 检查文件是否存在
ls -lh ~/.cookies/douyin_cookies.txt

# 检查文件内容格式
head -5 ~/.cookies/douyin_cookies.txt

# 确保是 Netscape 格式（制表符分隔）
```

### 问题 2：视频下载失败

**原因**：Cookies 可能过期

**解决**：重新获取 Cookies

### 问题 3：无法访问抖音

**原因**：网络限制

**解决**：
- 检查网络连接
- 某些地区可能需要代理

---

## 📚 相关文档

- [方案 1 详细指南](douyin-login-guide.md)
- [方案对比](douyin-cookies-solutions.md)
- [快速开始](../scripts/douyin-quickstart.sh)

---

## ✅ 检查清单

- [ ] 已在浏览器中登录抖音（手机扫码）
- [ ] 已安装浏览器扩展
- [ ] 已导出 Cookies 文件
- [ ] 已复制到 `~/.cookies/douyin_cookies.txt`
- [ ] 已验证 Cookies 有效
- [ ] 可正常处理抖音视频

---

**最后更新**：2026-04-04  
**版本**：v0.1.4
