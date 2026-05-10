# Magia-timeline自用修改版

原始英文readme：[README.md](https://github.com/HurryPeng/MagiaTimeline/blob/1.1/README.md)

原始中文readme：[README-zh_CN.md](https://github.com/HurryPeng/MagiaTimeline/blob/1.1/README-zh_CN.md)

为项目自用方便，将修改内容汇总至此，便于其他用户参考（项目修改和总结文本由GPT-5.5生成）。

# 修改内容

以下内容汇总当前项目基线版本（1.1.0-beta.6）以及本自用fork在其上的改动。重点记录用户可见行为、配置项、依赖条件和适用范围。

## 当前基线：1.1.0-beta.6

版本来源：`Version.py`

### GUI 工作流改进

- GUI 新增时间轴滑条和异步取帧，视频预览与时间跳转更顺滑。
- 字幕区域选择从旧版四个滑条改为视频画面上的可拖拽、可缩放矩形框。
- beta.6 基线中加入了打字机字幕支持和 SRT 输出相关 GUI 控件。

使用条件：

- GUI 仍属于实验性界面，主要面向默认 `dtd` 策略组。
- 必须先打开视频，才能拖拽字幕区域矩形框。
- 打字机字幕支持只影响 `dtd.default` 预设，并且需要启用 `dtd.default.enableTypewriter`（GUI中的`Enable Typewriter support`）。

### SRT 输出支持

- 通过 `outputSrt` 新增 SRT 字幕输出。
- 未启用 SRT 时仍保持旧行为：默认输出 ASS。

使用条件：

- `outputSrt: false` 只输出 ASS。
- `outputSrt: true` 同时输出 ASS 和 SRT。
- SRT 只保留普通字幕时间轴和文本，不保留 ASS 样式信息。

### DTD 算法更新

- 新增对打字机字幕，也就是逐字/逐段出现字幕的检测支持。
- 将对话特征整理为结构化的 `DialogFeature` 数据。
- 调整合并/拆分判断逻辑，增加 Sobel、inpaint、OCR、投影覆盖率、公共边缘移除等判定指标。
- 新增 `enableShortCircuit`，允许在最终 OCR 阶段前提前作出合并/拆分判断。
- 将 `boxVerticalExpansion` 重命名为 `boxExpansion`。
- 非主文本框抑制逻辑改为相对最大文本框面积进行比较。
- 扩展 DTD debug 日志字段，便于分析误合并、误拆分等问题。

使用条件：

- 这些算法变化主要适用于 `strategy: dtd`。
- 打字机字幕处理需要设置 `dtd.default.enableTypewriter: true`。
- 提前判定逻辑需要设置 `dtd.default.enableShortCircuit: true`。
- 旧配置中的 `boxVerticalExpansion` 需要迁移为 `boxExpansion`。

### 分辨率限制调整

- 将旧的单一 `maxResolution` 拆分为 `maxResWidth` 和 `maxResHeight`。
- 默认配置为 `maxResWidth: 2000`、`maxResHeight: 1200`，对竖屏视频会更积极地降采样。

使用条件：

- 任一轴设置为 `0` 表示不限制该轴。
- 视频会按 2 倍比例反复缩小，直到宽高都满足启用的限制。
- 旧配置中的 `maxResolution` 需要迁移为 `maxResWidth` 和 `maxResHeight`。

### Speculative engine 与 extra jobs

- speculative engine 在 interval 增长过程中持续刷新聚合特征，并在 interval 结束时写入磁盘缓存。
- extra-job frame 会优先保留 interval 中时间更靠后的帧，更适合 interval 增长后的 OCR/style 后处理。
- 增加 extra jobs 的运行保护：目前只允许在 speculative engine 下执行。
- OCR extra job 会输出待处理 interval 数量。

使用条件：

- `extraJobs` 目前只支持 `engine: speculative`。
- 策略本身必须实现 extra-job 支持。
- `extraJobs` 有效值为 `ocr` 和 `sty`。

### ASS 对比工具

- 新增 `DiffAss.py`，用于比较标准 ASS 与试验 ASS。
- 可将时间轴差异分类为 merge、split、missing、extra。

使用条件：

- 命令行传入两个 ASS 文件，顺序为标准文件在前、试验文件在后。
- 可通过 `--toleranceCs` 和 `--noiseMaxCs` 调整匹配容差和噪声阈值。

## 本自用分支改动

### 显式输出格式选择

- 新增 `outputFormat`，可选值：
  - `ass`：只输出 `.ass`。
  - `srt`：只输出 `.srt`。
  - `both`：同时输出 `.ass` 和 `.srt`。
- 在 `MagiaTimeline.py` 中新增 `resolveOutputFormat(config)`。
- 保留 `outputSrt` 作为兼容旧配置的回退逻辑。
- 默认 `config.yml` 改为 `outputFormat: srt`。

使用条件：

- `outputFormat` 优先级高于 `outputSrt`。
- 如果省略 `outputFormat`，继续沿用旧逻辑：`outputSrt: false` 表示只输出 ASS，`outputSrt: true` 表示 ASS 与 SRT 都输出。
- 只有请求 ASS 输出时才读取 `assTemplate`。
- SRT-only 模式适合只需要打轴结果、不需要 ASS 样式的 GUI 工作流。

### GUI 优先的 SRT 工作流

由于后续需要删除多余时间轴，相关调整软件只能输入`srt`格式，因此做出以下调整：

- GUI 启动处理时固定设置 `outputFormat: srt`。
- GUI 隐藏 OCR、样式分类、额外 SRT 输出控件（样式匹配和字幕识别工作由[GVS2](https://github.com/kiriya55/GVS2)项目负责）。
- GUI 固定设置 `extraJobs` 为空列表。
- GUI 在存在 `framewise` 配置时强制设置 `framewise.debug = false`，避免 OpenCV debug 窗口阻塞 GUI 流程。
- 新增启动脚本：
  - `MagiaTimeline-GUI.bat`：Windows 虚拟环境启动脚本。
  - `MagiaTimeline-GUI.sh`：GNU/Linux 或 macOS 虚拟环境启动脚本。

使用条件：

- GUI 适合“只输出 SRT 时间轴”的使用场景。
- 如果需要 ASS 样式、OCR 文本提取或样式分类，应使用命令行流程。
- 启动脚本假设项目根目录下存在本地 `venv`。

### GUI 输入视频格式扩展

受到Youtube下载格式影响，调整了一下GUI可接受格式

- GUI 文件选择器从只接受 `.mp4` 扩展为接受 `.mp4`、`.mkv`、`.webm`。
- GUI 视频时长检测增加回退逻辑：优先使用帧数，其次使用 stream duration，最后使用 container duration。

使用条件：

- 预览和 seek 仍依赖 PyAV 能够解码所选视频。
- 时间戳异常或封装不稳定的视频可能仍需要下面的自动 fallback 流程。

### GUI 自动视频 fallback 流程

- 新增 `VideoPreprocess.py`，集中处理 ffmpeg 修复命令构建和执行。
- GUI worker 现在最多尝试三轮处理：
  1. 直接处理原始视频。
  2. 如果失败，将视频 remux 为临时 MP4，并重新生成 presentation timestamps 后重试。
  3. 如果仍失败，将视频 re-encode 为临时恒定帧率 MP4 后重试。
- re-encode 优先选择可用 GPU H.264 编码器，顺序为 `h264_nvenc`、`h264_amf`、`h264_qsv`。
- 如果 GPU re-encode 失败，会回退到 CPU `libx264`。
- remux 成功后仍沿用原始字幕输出前缀。
- re-encode 成功后，字幕输出前缀改为原视频旁边的 `*.magiatimeline-reencoded`。

使用条件：

- 该 fallback 流程目前只接入 GUI worker。
- 系统必须安装 `ffmpeg`，并且 `ffmpeg` 需要位于 `PATH` 中。
- remux 要求源文件的音视频/字幕流足够兼容 MP4 stream copy。
- re-encode 要求 ffmpeg 至少有一个可用 H.264 编码器；最终回退为 CPU `libx264`。
- 临时修复视频写入 GUI 临时目录。
- re-encoded 字幕输出会写在原视频同目录，并带有 `magiatimeline-reencoded` 后缀。

### 测试覆盖

- 新增输出格式解析测试。
- 新增视频预处理测试，覆盖路径派生、ffmpeg 命令构建、编码器选择和 ffmpeg 输出解码。

验证命令：

- `python -m unittest discover -s tests -v`
- `python -m py_compile MagiaTimeline-GUI.py MagiaTimeline.py VideoPreprocess.py`
