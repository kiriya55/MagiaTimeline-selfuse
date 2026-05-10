from __future__ import annotations

import dataclasses
import pathlib
import subprocess
import typing


FFMPEG_EXE = "ffmpeg"


@dataclasses.dataclass(frozen=True)
class VideoPreprocessPaths:
    remuxed: pathlib.Path
    reencoded: pathlib.Path
    reencoded_destination: pathlib.Path

    @classmethod
    def from_source(cls, source: pathlib.Path, temp_dir: pathlib.Path) -> "VideoPreprocessPaths":
        stem = source.stem
        return cls(
            remuxed=temp_dir / f"{stem}.magiatimeline-remux.mp4",
            reencoded=temp_dir / f"{stem}.magiatimeline-reencoded.mp4",
            reencoded_destination=source.with_name(f"{stem}.magiatimeline-reencoded"),
        )


def build_remux_command(src: str, dst: str) -> typing.List[str]:
    return [
        FFMPEG_EXE,
        "-y",
        "-fflags",
        "+genpts",
        "-i",
        src,
        "-map",
        "0",
        "-c",
        "copy",
        dst,
    ]


def choose_h264_encoder(ffmpeg_encoders_output: str) -> str:
    for encoder in ("h264_nvenc", "h264_amf", "h264_qsv"):
        if encoder in ffmpeg_encoders_output:
            return encoder
    return "libx264"


def detect_h264_encoder() -> str:
    try:
        result = subprocess.run(
            [FFMPEG_EXE, "-hide_banner", "-encoders"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except OSError:
        return "libx264"
    output = decode_process_output(result.stdout)
    return choose_h264_encoder(output)


def build_reencode_command(src: str, dst: str, encoder: str) -> typing.List[str]:
    command = [
        FFMPEG_EXE,
        "-y",
        "-fflags",
        "+genpts",
        "-i",
        src,
        "-map",
        "0",
        "-fps_mode",
        "cfr",
        "-c:v",
        encoder,
    ]
    if encoder == "libx264":
        command += ["-preset", "veryfast", "-crf", "18"]
    command += [
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "copy",
        "-c:s",
        "copy",
        dst,
    ]
    return command


def run_ffmpeg(command: typing.List[str]) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except OSError as exc:
        return subprocess.CompletedProcess(command, 1, stdout=str(exc))
    return subprocess.CompletedProcess(
        command,
        result.returncode,
        stdout=decode_process_output(result.stdout),
    )


def decode_process_output(output: typing.Any) -> str:
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")
    if output is None:
        return ""
    return str(output)
