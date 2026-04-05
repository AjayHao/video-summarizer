# Changelog

## v0.1.3 (2026-04-04)

### 🚀 新增功能

- **小红书支持优化**：
  - 优化 `download-audio.sh` 脚本，增加平台检测
  - 针对小红书使用 `best` 格式下载（无单独音频流）
  - 三阶段降级策略，确保下载成功率
  - 实测验证：10 分钟视频完整处理成功（http://xhslink.com/o/6asTvoRsCk2）

- **封面图上传功能**：
  - `upload-to-oss.py` 新增 `thumbnail` 模式
  - `video-summarize.sh` Step 7 增加封面上传步骤
  - 自动更新 `metadata.json` 中的 `thumbnail` 字段
  - 解决小红书等平台封面防盗链问题

### 🐛 Bug 修复

- **元数据提取优化**：
  - 作者：从 `uploader_id` 转换为可读名称（如"小红书用户"）
  - 时长：从 `duration` 秒数转换为 `MM:SS` 格式（如"10:06"）
  - 适配小红书等平台元数据字段

### 📊 平台支持更新

- ✅ Bilibili/YouTube：完整支持
- ✅ 小红书：基本支持（Plan B + 封面上传）
- 🚧 抖音：待测试（计划 v0.1.4）

---

## ✅ v0.1.4 (2026-04-05)

### 🚀 新增功能

- **抖音完整支持（无需 Cookies）**：
  - 整合 agent-reach 抖音下载工具
  - 复制 `douyin_downloader.py` 到 scripts/
  - 修改 `video-summarize.sh` 自动识别抖音平台
  - 使用专用工具下载（无需 Cookies，无反爬）
  - 后续流程不变（Plan B + AI 分析 + 截图 + Notion）

### 🐛 Bug 修复

- **标题优化**：
  - 从标题中移除 `#标签`（分离到 Tags 字段）
  - 长标题智能截断（保留前 2-3 分句，添加 `...`）
  - 标题长度：158 字符 → 26 字符

- **封面图片修复**：
  - 优先使用 OSS 截图（永久有效，避免抖音签名 URL 过期）
  - 优先级：`![视频封面](URL)` → 第一张章节截图 → metadata.json thumbnail

- **Tags 修复**：
  - 从 metadata.json 原始标题提取 `#标签`
  - 修复前：固定默认标签
  - 修复后：AI 视频，AI 动画，AI 电影，AIGC，AI 教程

### 🧹 代码清理

- 删除冗余脚本：
  - `douyin_processor.py` - MCP 服务器，主流程未使用
  - `douyin-login-v2.sh` - v0.1.4 无需 Cookies，功能废弃

### 📊 平台支持更新

- ✅ Bilibili/YouTube：完整支持
- ✅ 小红书：基本支持（Plan B）
- ✅ **抖音：完整支持（无需 Cookies）**
- 🚧 微信视频号：待测试

---

## ✅ v0.1.5 (2026-04-05)

### 🚀 新增功能

- **并行优化**：
  - Step 2 (字幕下载) 和 Step 4 (视频下载) 并行执行
  - 节省约 30 秒 (32%↓)，总耗时从 180 秒降至 150 秒
  - 使用 `wait` 等待两个任务完成后继续

- **标签提取策略升级**：
  - 四层策略：标题 hashtag → 元数据 tags → AI 关键词 → 默认值
  - 从视频标题提取 `#([\w\u4e00-\u9fa5]+)` hashtag
  - 标签长度放宽至 2-15 字符 (兼容英文如 "openclaw")
  - Notion 推送从 Markdown `**Tags:**` 行解析标签

- **GPU 自适应**：
  - `transcribe-audio.py` 新增 GPU 检测函数
  - 根据显存自动选择 Faster-Whisper 模型
  - GPU ≥8GB → large-v2, ≥4GB → medium, ≥2GB → small, 无 GPU → base (CPU)

- **日志系统完善**：
  - 新增 `log_debug()` 级别
  - 错误日志输出到 `$OUTPUT_DIR/error.log`
  - 支持 `--verbose` 模式查看调试信息

### 🐛 Bug 修复

- **OSS 路径修复**：
  - 修复 `upload-to-oss.py` prefix 拼接缺失 `/` 分隔符问题
  - 路径规范：`screenshots/{platform}/{video_id}_{timestamp}/{filename}`
  - 使用 `auto` 模式自动生成正确路径

- **标签解析修复**：
  - 修复抖音/小红书分支标签解析缺失
  - 统一各平台标签提取逻辑为三层策略
  - 优化 B 站标题清理逻辑

- **抖音短链接支持**：
  - 新增 `v.douyin.com` 短链接识别
  - 平台识别失败返回 `'unknown'` 而非 `None`

### 🗑️ 删除功能

- **删除微信视频号支持**：
  - 微信视频号已不支持外链访问
  - 移除 `wxvideo` 平台识别逻辑
  - 聚焦四大平台：B 站、YouTube、抖音、小红书

### 📊 平台支持更新

- ✅ Bilibili/YouTube：完整支持
- ✅ 小红书：基本支持 (Plan B + 封面上传)
- ✅ 抖音：完整支持 (无需 Cookies)
- ❌ 微信视频号：已移除 (不支持外链)

---

## v0.1.2 (2026-04-04)

### 🐛 Bug 修复

- **修复 Markdown 渲染错误**：
  - `analyze-subtitles-ai.py` 第 461 行变量名错误
  - `metadata.get('tags', [])` → `video_info.get('tags', [])`
  - 解决了生成总结时的 `NameError` 异常

### 🔄 步骤顺序优化

- **调整 `video-summarize.sh` 执行流程**，逻辑更清晰：
  - Step 5: AI 分析（从 Step 7 提前，为截图提供时间戳）
  - Step 6: 截图（基于 AI 分析结果的关键时间点）
  - Step 7: OSS 上传
  - Step 8: 渲染 Markdown
  - Step 9: 整理输出
- **改进截图逻辑说明**：注释从"基于内容时间戳"改为"基于 AI 分析结果"

### 🛡️ 错误处理增强

- **新增日志级别函数**：
  - `log_info()` - 信息日志
  - `log_warn()` - 警告日志
  - `log_error()` - 错误日志
- **新增错误捕获 trap**：
  - 脚本失败时自动输出错误日志路径
  - 显示详细错误信息（verbose 模式）
- **AI 分析失败降级**：
  - 不再直接退出，生成空 AI 结果继续执行
  - 截图使用均匀分布兜底
  - 最终总结使用基础版本

### 📝 文档与配置更新

- 更新 `README.md` 和 `SKILL.md` 的版本号为 v0.1.2
- 更新 `README.md` 发布日期为 2026-04-04
- 更新 `prompt.json` 版本号为 v0.1.2
- 统一所有脚本权限为 755（可执行）
- **新增平台支持状态说明**：
  - ✅ Bilibili/YouTube 完整支持
  - 🚧 小红书/抖音/微信视频号待完善（Plan B 可用）

---

## v0.1.1 (2026-03-31)

### 🛠️ 优化

- **标签信息优化**：Notion 标签现在直接使用视频原始标签，尊重视频作者对视频的分类定义
  - 修改 `analyze-subtitles-ai.py` 中标签生成逻辑
  - 从 metadata.json 提取视频原始标签（tags 字段）
  - 筛选 2-6 字符的高质量标签，去重后取前 5 个
  - 不足 5 个时用默认标签补齐（视频总结、AI 分析、教程、技巧、知识分享）
  - 不再强制插入"视频总结"前缀，完全保留作者意图

### 🧹 清理

- 删除冗余脚本（5 个）：
  - `video-summarize-oss.sh` - 旧版主流程，功能已被覆盖
  - `analyze-subtitles.py` - 旧版简单分析，已被 AI 版替代
  - `upload-to-qiniu.py` - 七牛云上传（未启用）
  - `finalize-and-push.sh` - 旧版推送预览，已内化到主脚本
  - `fetch.sh` - 旧版元数据获取，已内化到主脚本
- 保留 Plan B 脚本（`download-audio.sh`、`transcribe-audio.py`）

### 📊 效果对比

**修改前**：
```
标签：视频总结、AI 分析、教程、技巧、知识分享（固定默认值）
```

**修改后**（以 BV1cGigBQE6n 为例）：
```
标签：原理、AI、教程、claude、大模型（来自视频原始标签）
```

---

## v0.1.0 (2026-03-28)

### ✨ 初始版本

- 四阶段架构（素材准备 → 加工提炼 → 内容整合 → 输出交付）
- 断点续跑支持
- 截图嵌入（最多 30 张）
- 阿里云 OSS 图床集成
- Notion 推送
- Plan A/B 双模式（官方字幕 / 语音转录）

---

## 🔜 v0.1.6 (计划中)

### 🎯 版本定位
**代码重构 + 测试覆盖**

### 📋 计划内容

**高优先级**：
- [ ] 重构 `push-to-notion.py`（提取平台分支为独立函数）
- [ ] 添加单元测试（核心函数覆盖率 80%+）
- [ ] 完善错误处理和日志（结构化日志格式）

**中优先级**：
- [ ] 性能优化（截图并行上传、结果缓存）
- [ ] 文档完善（API 参考、故障排查手册）

**低优先级**：
- [ ] 支持更多平台（TikTok、Instagram Reels）
- [ ] Web UI（可选）
