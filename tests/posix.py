import os
import platform
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


EXECUTABLE = Path(__file__).resolve().parents[1] / "fetch"


class FetchTests(unittest.TestCase):
    def run_fetch(self, args, home=None):
        env = os.environ.copy()
        if home:
            env["HOME"] = str(home)
        return subprocess.run(
            [str(EXECUTABLE), *args], env=env, capture_output=True, timeout=10
        )

    def test_help_and_version(self):
        self.assertIn(b"Usage:", self.run_fetch(["--help"]).stdout)
        self.assertIn(platform.system().encode(), self.run_fetch(["--version"]).stdout)

    def test_invalid_arguments(self):
        for args in [
            ["--frames", "-1"], ["--frames", "junk"], ["--frames", "2147483648"],
            ["--frames", "1.5"], ["--height", "0"], ["--height", "201"],
            ["--size", "nan"], ["--size", "0.4"], ["--size", "5.1"],
            ["--depth", "inf"], ["--depth", "0"], ["--depth", "10.1"],
            ["--speed", "1junk"], ["--speed", "1e9999"], ["--speed", "1001"],
            ["--logo"], ["--unknown"],
        ]:
            with self.subTest(args=args):
                result = self.run_fetch(args)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr)

    def test_shading_and_cli_precedence(self):
        with tempfile.TemporaryDirectory(prefix="fetch-test-") as directory:
            home = Path(directory)
            config_dir = home / ".config" / "fetch"
            config_dir.mkdir(parents=True)
            (config_dir / "logo.txt").write_text("  @@  \n@@@@@@\n  @@  \n", encoding="utf-8")
            config = config_dir / "config"
            config.write_text("size=1\ndepth=1\nspeed=1\nheight=20\n")
            args = ["--no-info", "--frames", "3", "--no-color"]
            baseline = self.run_fetch(args, home)
            self.assertEqual(baseline.returncode, 0)
            self.assertNotIn(b"\x00", baseline.stdout)
            config.write_text("size=2\ndepth=2\nspeed=2\nheight=30\n")
            override = self.run_fetch(
                args + ["--size", "1", "--depth", "1", "--speed", "1", "--height", "20"], home
            )
            self.assertEqual(override.stdout, baseline.stdout)
            for mode in ["ascii", "blocks", "sextants"]:
                with self.subTest(mode=mode):
                    result = self.run_fetch(args + ["--shading-mode", mode], home)
                    self.assertEqual(result.returncode, 0)
                    self.assertTrue(result.stdout)

    def test_zero_and_negative_config_speed(self):
        with tempfile.TemporaryDirectory(prefix="fetch-test-") as directory:
            home = Path(directory)
            config_dir = home / ".config" / "fetch"
            config_dir.mkdir(parents=True)
            (config_dir / "logo.txt").write_text("  @@  \n@@@@@@\n  @@  \n")
            config = config_dir / "config"
            args = ["--no-info", "--frames", "3", "--no-color"]
            for speed in ["0", "-20"]:
                with self.subTest(speed=speed):
                    config.write_text("speed=20\n")
                    baseline = self.run_fetch(args + ["--speed", speed], home)
                    config.write_text(f"speed={speed}\n")
                    configured = self.run_fetch(args, home)
                    self.assertEqual(baseline.returncode, 0)
                    self.assertEqual(configured.returncode, 0)
                    self.assertEqual(configured.stdout, baseline.stdout)

    def test_rotation_cli_precedence(self):
        with tempfile.TemporaryDirectory(prefix="fetch-test-") as directory:
            home = Path(directory)
            config_dir = home / ".config" / "fetch"
            config_dir.mkdir(parents=True)
            (config_dir / "logo.txt").write_text("  @@  \n@@@@@@\n  @@  \n")
            config = config_dir / "config"
            args = ["--no-info", "--frames", "3", "--no-color", "--speed", "20"]
            for axis, config_axis in [("x", "y"), ("y", "x")]:
                with self.subTest(axis=axis):
                    config.write_text("")
                    baseline = self.run_fetch(args + [f"--rotate-{axis}"], home)
                    config.write_text(f"spin={config_axis}\n")
                    override = self.run_fetch(args + [f"--rotate-{axis}"], home)
                    self.assertEqual(baseline.returncode, 0)
                    self.assertEqual(override.returncode, 0)
                    self.assertEqual(override.stdout, baseline.stdout)

    def test_invalid_config_numbers(self):
        with tempfile.TemporaryDirectory(prefix="fetch-test-") as directory:
            home = Path(directory)
            config_dir = home / ".config" / "fetch"
            config_dir.mkdir(parents=True)
            (config_dir / "logo.txt").write_text("  @@  \n@@@@@@\n  @@  \n")
            config = config_dir / "config"
            args = ["--no-info", "--frames", "3", "--no-color"]
            baseline = self.run_fetch(args, home)
            self.assertEqual(baseline.returncode, 0)
            for key, value in [("height", "0"), ("size", "nan"),
                               ("depth", "inf"), ("speed", "1junk")]:
                with self.subTest(key=key):
                    config.write_text(f"{key}={value}\n")
                    result = self.run_fetch(args, home)
                    self.assertEqual(result.returncode, 0)
                    self.assertIn(key.encode(), result.stderr)
                    self.assertEqual(result.stdout, baseline.stdout)

    def test_minimal_logos(self):
        with tempfile.TemporaryDirectory(prefix="fetch-test-") as directory:
            home = Path(directory)
            config_dir = home / ".config" / "fetch"
            config_dir.mkdir(parents=True)
            for logo in ["@\n", "@@@\n", "@\n@\n@\n"]:
                with self.subTest(logo=logo):
                    (config_dir / "logo.txt").write_text(logo)
                    result = self.run_fetch(["--no-info", "--frames", "1"], home)
                    self.assertEqual(result.returncode, 0)
                    self.assertTrue(result.stdout)

    def test_labels_take_the_logo_color(self):
        # The labels wear the color the logo is drawn in. Without fastfetch
        # there is no colored logo, so they fall back to the brand color.
        has_fastfetch = shutil.which("fastfetch") is not None
        logos = {
            "arch": ("\x1b[1;36m", "\x1b[1;38;2;0;170;238m"),
            "ubuntu": ("\x1b[1;31m", "\x1b[1;38;2;233;84;32m"),
            "bazzite": ("\x1b[1;36m", "\x1b[1;38;2;138;43;226m"),
            "redhat": ("\x1b[1;31m", "\x1b[1;38;2;238;0;0m"),
            "linuxmint": ("\x1b[1;32m", "\x1b[1;38;2;134;190;67m"),
            "fedora": ("\x1b[1;34m", "\x1b[1;38;2;60;110;180m"),
            "gentoo": ("\x1b[1;35m", "\x1b[1;38;2;122;108;179m"),
        }
        with tempfile.TemporaryDirectory(prefix="fetch-test-") as directory:
            home = Path(directory)
            for logo, escapes in logos.items():
                with self.subTest(logo=logo, fastfetch=has_fastfetch):
                    escape = escapes[0] if has_fastfetch else escapes[1]
                    result = self.run_fetch(["--frames", "1", "--logo", logo], home)
                    self.assertEqual(result.returncode, 0)
                    self.assertIn((escape + "OS").encode(), result.stdout)

    def test_logo_and_labels_share_one_color(self):
        # The logo keeps its own colors and the labels wear the same one.
        has_fastfetch = shutil.which("fastfetch") is not None
        escape = "\x1b[1;36m" if has_fastfetch else "\x1b[1;38;2;0;170;238m"
        with tempfile.TemporaryDirectory(prefix="fetch-test-") as directory:
            home = Path(directory)
            result = self.run_fetch(["--frames", "1", "--logo", "arch"], home)
            self.assertEqual(result.returncode, 0)
            self.assertIn((escape + "OS").encode(), result.stdout)
            # The logo itself is painted in it too, not just the labels.
            self.assertGreater(result.stdout.count(escape.encode()), 1)

    def test_colorless_logo_falls_back_to_brand_color(self):
        # A custom logo without colors of its own gets the brand color, and
        # the labels go along with it.
        with tempfile.TemporaryDirectory(prefix="fetch-test-") as directory:
            home = Path(directory)
            config_dir = home / ".config" / "fetch"
            config_dir.mkdir(parents=True)
            (config_dir / "logo.txt").write_text("# distro: bazzite\n  @@  \n@@@@@@\n")
            result = self.run_fetch(["--frames", "1"], home)
            self.assertEqual(result.returncode, 0)
            self.assertIn(b"\x1b[1;38;2;138;43;226mOS", result.stdout)
            self.assertGreater(result.stdout.count(b"\x1b[1;38;2;138;43;226m"), 1)

    def test_label_color_config_overrides_distro(self):
        with tempfile.TemporaryDirectory(prefix="fetch-test-") as directory:
            home = Path(directory)
            config_dir = home / ".config" / "fetch"
            config_dir.mkdir(parents=True)
            (config_dir / "config").write_text("os\nhost\nlabel_color=green\n")
            result = self.run_fetch(["--frames", "1", "--logo", "ubuntu"], home)
            self.assertEqual(result.returncode, 0)
            self.assertIn(b"\x1b[1;32mOS", result.stdout)
            self.assertNotIn(b"\x1b[1;38;2;233;84;32mOS", result.stdout)

    def test_truecolor_fallback(self):
        with tempfile.TemporaryDirectory(prefix="fetch-test-") as directory:
            home = Path(directory)
            config_dir = home / ".config" / "fetch"
            config_dir.mkdir(parents=True)
            (config_dir / "config").write_text("os\nhost\ntruecolor=0\n")
            result = self.run_fetch(["--frames", "1", "--logo", "arch"], home)
            self.assertEqual(result.returncode, 0)
            self.assertIn(b"\x1b[1;36mOS", result.stdout)
            self.assertNotIn(b"\x1b[1;38;2;", result.stdout)

    def test_no_color_strips_every_color(self):
        with tempfile.TemporaryDirectory(prefix="fetch-test-") as directory:
            home = Path(directory)
            result = self.run_fetch(["--frames", "1", "--no-color", "--logo", "arch"], home)
            self.assertEqual(result.returncode, 0)
            # Only cursor control sequences may remain, no SGR colors.
            self.assertNotIn(b"\x1b[0m", result.stdout)
            self.assertNotIn(b"\x1b[1;", result.stdout)

    def test_program_name_follows_argv(self):
        # "make install" also installs the binary as "3dfetch"; the tool
        # should report the name it was invoked with.
        with tempfile.TemporaryDirectory(prefix="fetch-test-") as directory:
            alias = Path(directory) / "3dfetch"
            alias.symlink_to(EXECUTABLE)
            result = subprocess.run(
                [str(alias), "--help"], capture_output=True, timeout=10
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn(b"Usage: 3dfetch", result.stdout)


if __name__ == "__main__":
    unittest.main()
