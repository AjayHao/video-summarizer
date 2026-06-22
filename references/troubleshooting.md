# 故障排查

> 本文档为 [SKILL.md](../SKILL.md) 的补充参考，记录常见问题与解决方案。

---

## Cookies 过期（B 站）

```bash
# 重新扫码登录
./bili-login.sh
```

## 配置检查

```bash
# 运行检查脚本
./check-config.sh
```

## 查看详细日志

```bash
# 使用 verbose 模式
./video-summarize.sh "URL" --verbose

# 查看错误日志
cat <output_dir>/error.log
```

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 截图 404 | OSS 路径不匹配 | `python3 upload-to-oss.py auto <output_dir>` |
| 标签默认值 | 标签提取失败 | 检查标题 hashtag 格式 `#标签` |
| 转录失败 | 无 GPU/API 配额 | 检查 `GROQ_API_KEY`，或确保 `faster-whisper` 已安装 |
| Notion 推送失败 | API Key 过期 | 更新 `NOTION_API_KEY`（可选功能，仅 --push 需要） |
| 并行任务失败 | 依赖缺失 | 检查 `ffmpeg` / `yt-dlp` 安装（版本要求：ffmpeg >= 6.1, yt-dlp >= 2026.03.17） |
| 抖音下载失败 | 链接格式错误 | 使用完整 URL 或 v.douyin.com 短链 |
| 抖音文案提取失败 | 无 API Key | `douyin_downloader.py` 会自动降级到本地 Faster-Whisper，无需单独配置 |

## 依赖版本检查

```bash
# 检查核心依赖版本
ffmpeg -version | head -1    # 应 >= 6.1
yt-dlp --version             # 应 >= 2026.03.17
python3 --version            # 应 >= 3.9

# 检查 Python 包
python3 -c "import requests; print('requests:', requests.__version__)"
python3 -c "import oss2; print('oss2:', oss2.__version__)"
python3 -c "import dotenv; print('dotenv installed')"
```
