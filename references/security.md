# 安全与隐私说明

> 本文档为 [SKILL.md](../SKILL.md) 的补充参考，记录安全与隐私相关信息。

---

## 敏感数据处理

| 文件/路径 | 用途 | 敏感性 | 用户控制 |
|-----------|------|--------|----------|
| `~/.cookies/bilibili_cookies.txt` | B 站官方字幕获取 | 高（Session Token） | 用户主动扫码生成，可随时删除 |
| `$AGENT_HOME/.env` | API Keys 存储 | 高 | 用户自行配置，skill 不修改 |
| `<临时目录>/video-summarizer-*/` | 临时输出 | 低 | 处理完成后可手动清理 |

## 外部服务端点

| 服务 | 域名 | 用途 | 传输数据 |
|------|------|------|----------|
| LLM 平台 (可配置) | 通过 LLM_BASE_URL 指定 | AI 分析 | 字幕文本、元数据 |
| 阿里云 OSS | `oss-cn-shanghai.aliyuncs.com` | 图床上传 | 截图、封面图 |
| Groq | `api.groq.com` | 备用转录（可选，需代理） | 音频片段 |
| Bilibili | `bilibili.com` | 视频下载/字幕 | 无（仅下载） |
| YouTube | `youtube.com` | 视频下载/字幕 | 无（仅下载） |
| 抖音 | `douyin.com` / `iesdouyin.com` | 视频下载 | 无（仅下载） |

**说明**: 
- LLM 平台由用户通过 `LLM_BASE_URL` 控制，支持任意 OpenAI 兼容接口（DeepSeek / DashScope / OpenAI / Groq 等）
- Groq API 为可选加速方案，未配置时自动降级到本地 Faster-Whisper

## 最小权限建议

- **OSS Bucket**: 创建专用 Bucket，仅授予 PutObject/GetObject 权限
- **API Keys**: 使用子账号 Key，设置 IP 白名单
- **测试环境**: 首次使用建议在隔离环境测试

## ⚠️ 数据流向提醒

- **LLM 平台（可配置）**: 字幕文本和视频元数据会发送至用户配置的 LLM 服务，请勿处理包含敏感信息的视频
- **Groq（可选）**: 音频片段会发送至 Groq API（加速转录），未配置时自动降级为本地 Faster-Whisper
- **阿里云 OSS**: 截图和封面图上传至 OSS Bucket，建议配置为专用 Bucket 并设置为私有读/写
- **Notion**: 总结结果推送至 Notion 数据库，确保 Integration 仅授予目标数据库权限
- **B 站 Cookies**: 扫码登录后存储于 `~/.cookies/bilibili_cookies.txt`，权限已限制为 600，仅限本机访问
- **Cookie 安全**: 登录完成后临时 `cookies.json` 会自动清理，不残留 skill 目录内
