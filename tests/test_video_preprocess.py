import pathlib
import subprocess
import unittest
from unittest import mock

from VideoPreprocess import (
    VideoPreprocessPaths,
    build_reencode_command,
    build_remux_command,
    choose_h264_encoder,
)


class VideoPreprocessTest(unittest.TestCase):
    def test_fixed_paths_are_derived_from_original_stem(self):
        paths = VideoPreprocessPaths.from_source(
            pathlib.Path(r"C:\media\clip.webm"),
            pathlib.Path(r"C:\tmp\MagiaTimeline_abc"),
        )

        self.assertEqual(paths.remuxed.name, "clip.magiatimeline-remux.mp4")
        self.assertEqual(paths.reencoded.name, "clip.magiatimeline-reencoded.mp4")
        self.assertEqual(paths.reencoded_destination.name, "clip.magiatimeline-reencoded")

    def test_remux_command_regenerates_pts_and_copies_streams(self):
        command = build_remux_command("input.webm", "fixed.mp4")

        self.assertEqual(command[:4], ["ffmpeg", "-y", "-fflags", "+genpts"])
        self.assertIn("-c", command)
        self.assertIn("copy", command)
        self.assertEqual(command[-1], "fixed.mp4")

    def test_choose_encoder_prefers_gpu_when_available(self):
        self.assertEqual(choose_h264_encoder(" V..... h264_nvenc\n V..... libx264\n"), "h264_nvenc")
        self.assertEqual(choose_h264_encoder(" V..... h264_amf\n V..... libx264\n"), "h264_amf")
        self.assertEqual(choose_h264_encoder(" V..... libx264\n"), "libx264")

    def test_reencode_command_uses_selected_encoder_and_cfr(self):
        command = build_reencode_command("input.mkv", "fixed.mp4", "h264_nvenc")

        self.assertIn("-fps_mode", command)
        self.assertIn("cfr", command)
        self.assertIn("-c:v", command)
        self.assertIn("h264_nvenc", command)
        self.assertEqual(command[-1], "fixed.mp4")

    def test_run_ffmpeg_decodes_non_gbk_output_without_crashing(self):
        from VideoPreprocess import run_ffmpeg

        completed = subprocess.CompletedProcess(
            ["ffmpeg"],
            1,
            stdout=b"\xff\xfe bad console bytes",
        )
        with mock.patch("subprocess.run", return_value=completed):
            result = run_ffmpeg(["ffmpeg", "-version"])

        self.assertEqual(result.returncode, 1)
        self.assertIn("bad console bytes", result.stdout)


if __name__ == "__main__":
    unittest.main()
