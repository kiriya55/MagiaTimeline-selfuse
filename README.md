# Magia-timeline自用修改版

## 当前基线：1.1.0-beta.7

版本来源：`Version.py`

# fork相关改动

### GUI 输入格式扩展

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
