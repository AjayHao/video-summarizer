# Video Summarizer

🎬 将 B 站/YouTube 视频转换为结构化 Notion 风格总结

## 快速开始

```bash
# 1. 获取视频元数据
~/.openclaw/skills/video-summarizer/scripts/fetch.sh "https://www.bilibili.com/video/BVxxx"

# 2. 使用模板生成总结
# 复制 templates/summary.md 并填充内容
```

## 依赖

- `yt-dlp` - 视频元数据获取
- `jq` - JSON 解析
- `bash` - 脚本运行

## 输出示例

查看 `templates/summary.md` 了解完整格式。

## 截图服务

视频帧截图使用 BibiGPT 服务：
```
https://bibigpt-apps.chatvid.ai/screenshots/{platform}/{videoId}/{timestamp}.jpg
```

## 文件结构

```
video-summarizer/
├── SKILL.md           # 技能说明
├── README.md          # 本文件
├── templates/
│   └── summary.md     # Markdown 模板
└── scripts/
    └── fetch.sh       # 元数据获取脚本
```

---

**版本:** 1.0  
**创建:** 2026-03-22
