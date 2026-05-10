import unittest

from MagiaTimeline import resolveOutputFormat


class OutputFormatTest(unittest.TestCase):
    def test_explicit_output_format_wins(self):
        self.assertEqual(resolveOutputFormat({"outputFormat": "srt", "outputSrt": False}), "srt")

    def test_legacy_output_srt_false_means_ass(self):
        self.assertEqual(resolveOutputFormat({"outputSrt": False}), "ass")

    def test_legacy_output_srt_true_means_both(self):
        self.assertEqual(resolveOutputFormat({"outputSrt": True}), "both")


if __name__ == "__main__":
    unittest.main()
