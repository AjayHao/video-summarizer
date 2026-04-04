# Snap 版本 Chromium 获取抖音 Cookies

## 📍 问题

Snap 版本的 Chromium 使用特殊的沙盒目录，yt-dlp 无法自动读取 Cookies。

---

## ✅ 解决方案：使用浏览器扩展

### 步骤 1：安装扩展

1. **打开 Chromium 浏览器**
   ```bash
   chromium-browser
   ```

2. **安装 Cookies 导出扩展**
   
   访问 Chrome 网上应用店，搜索并安装：
   - **扩展名称**：Get cookies.txt LOCALLY
   - **链接**：https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
   
   或者：
   - **扩展名称**：cookies.txt
   - **链接**：https://chromewebstore.google.com/detail/cookiestxt/mh0xfg3j7i6f8k2n1p4q5r6s7t8u9v0w

### 步骤 2：导出 Cookies

1. **访问抖音**
   ```
   https://www.douyin.com
   ```

2. **确认已登录**
   - 能看到用户头像
   - 能正常浏览视频

3. **点击扩展图标**
   - 在浏览器右上角找到扩展图标
   - 点击它

4. **导出 Cookies**
   - 点击 "Export" 或 "导出" 按钮
   - 保存为 `douyin_cookies.txt`

### 步骤 3：保存到正确位置

```bash
# 创建目录
mkdir -p ~/.cookies

# 移动文件（假设下载到了 Downloads 目录）
mv ~/Downloads/douyin_cookies.txt ~/.cookies/douyin_cookies.txt

# 或者如果是直接保存
# 保存时选择路径：/home/ajayhao/.cookies/douyin_cookies.txt
```

### 步骤 4：验证

```bash
# 检查文件
ls -lh ~/.cookies/douyin_cookies.txt

# 查看内容预览
head -10 ~/.cookies/douyin_cookies.txt

# 测试 Cookies
yt-dlp --cookies ~/.cookies/douyin_cookies.txt \
       --simulate \
       "https://v.douyin.com/bQ2chgMWotA/"
```

如果成功，会显示视频信息。

---

## 🚀 使用

Cookies 验证通过后：

```bash
cd ~/.openclaw/skills/video-summarizer/scripts

# 处理抖音视频
./video-summarize.sh "https://v.douyin.com/bQ2chgMWotA/"
```

---

## ⚠️ 注意事项

### Snap 权限

如果扩展无法访问 Cookies，可能需要授予权限：

```bash
# 连接 Snap 包到系统
sudo snap connect chromium:browser-support :browser-support
```

### 文件权限

```bash
chmod 600 ~/.cookies/douyin_cookies.txt
```

---

## 🔍 故障排查

### 问题 1：扩展无法导出

**解决**：
1. 确保已访问 douyin.com 并登录
2. 刷新页面后重试
3. 尝试其他扩展（如 EditThisCookie）

### 问题 2：yt-dlp 测试失败

**原因**：Cookies 可能过期或格式错误

**解决**：
1. 重新登录抖音
2. 重新导出 Cookies
3. 检查文件格式（应该是 Netscape 格式）

---

**最后更新**：2026-04-04
