"""Tests for the Phase C tooling: explain, completions, and the last two guides."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kiln import catalog as cat   # noqa: E402
from kiln import completions as compmod  # noqa: E402
from kiln import explain as explainmod   # noqa: E402
from kiln import guards           # noqa: E402

SPEC = ROOT / "specs" / "gallery" / "kanban.md"
CALC = ROOT / "specs" / "gallery" / "calculator.md"


class TestExplain(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_it_reports_the_pattern_and_the_capabilities(self):
        e = explainmod.explain(SPEC, self.c)
        self.assertTrue(e["ok"])
        self.assertEqual("kanban", e["pattern"])
        self.assertIn("board", e["features_emitted"])

    def test_the_size_is_measured_not_guessed(self):
        e = explainmod.explain(SPEC, self.c)
        self.assertGreater(e["size_bytes"], 20_000)
        self.assertEqual(round(e["size_bytes"] / 1024, 1), e["size_kb"])

    def test_a_calculator_reports_no_entity(self):
        e = explainmod.explain(CALC, self.c)
        self.assertEqual([], e["fields"])
        self.assertEqual("calculator", e["pattern"])

    def test_requires_are_reported_separately(self):
        e = explainmod.explain(CALC, self.c)
        self.assertIsInstance(e["features_added_by_requires"], list)

    def test_a_broken_spec_is_explained_not_crashed(self):
        with self.subTest():
            import tempfile
            bad = Path(tempfile.mkdtemp()) / "app-bad.md"
            bad.write_text("# Bad\n\n```json kiln\n{\"id\": \"app-bad\"}\n```\n", encoding="utf-8")
            e = explainmod.explain(bad, self.c)
            self.assertFalse(e["ok"])
            self.assertTrue(e["problems"])

    def test_the_text_rendering_names_the_output(self):
        text = explainmod.render(explainmod.explain(SPEC, self.c))
        self.assertIn("pattern", text)
        self.assertIn("checks", text)
        self.assertIn("KB", text)


class TestCompletions(unittest.TestCase):
    def setUp(self):
        self.parser = None

    def _parser(self):
        # the real parser, built the way main() builds it
        from kiln.cli import build_parser  # noqa: F401  (may not exist)
        return None

    def test_every_shell_renders(self):
        for shell in compmod.SHELLS:
            out = compmod.build(shell, _parser())
            self.assertGreater(len(out), 80, shell)

    def test_an_unknown_shell_is_refused(self):
        with self.assertRaises(ValueError):
            compmod.build("csh", _parser())

    def test_the_bash_output_is_valid_bash(self):
        if not shutil.which("bash"):
            self.skipTest("bash is not on PATH")
        out = compmod.build("bash", _parser())
        with __import__("tempfile").NamedTemporaryFile("w", suffix=".bash", delete=False) as f:
            f.write(out)
            path = f.name
        try:
            p = subprocess.run(["bash", "-n", path], capture_output=True, text=True)
        finally:
            Path(path).unlink(missing_ok=True)
        self.assertEqual(0, p.returncode, p.stderr)

    def test_every_subcommand_appears(self):
        out = compmod.build("bash", _parser())
        for sub in ("build", "verify", "explain", "adopt", "licence"):
            self.assertIn(sub, out)


def _parser():
    """Build the CLI parser without running a command."""
    import kiln.cli as cli
    import argparse
    if hasattr(cli, "_build_parser"):
        return cli._build_parser()
    # main() builds it inline; reproduce the call by running --help through it
    import io
    import contextlib
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            cli.main(["--help"])
    except SystemExit:
        pass
    # the parser is reachable through a completions run
    ap = None
    from kiln import cli as c
    src = Path(c.__file__).read_text(encoding="utf-8")
    self_check = "args._parser = ap" in src
    assert self_check, "the CLI no longer exposes its parser"
    return _parser_from_module()


def _parser_from_module():
    """Ask the CLI for its parser by calling completions with a stub namespace."""
    import argparse
    import kiln.cli as cli
    # run main() with completions and capture the parser it used
    captured = {}
    real = cli.cmd_completions

    def spy(args, catalog=None):
        captured["parser"] = args._parser
        return 0
    cli.cmd_completions = spy
    try:
        cli.main(["completions", "bash"])
    finally:
        cli.cmd_completions = real
    return captured["parser"]


class TestTheEightGuides(unittest.TestCase):
    def test_all_eight_exist(self):
        self.assertEqual(8, len(guards.GUIDES))
        for name in guards.GUIDES:
            p = ROOT / name
            self.assertTrue(p.exists(), name)
            self.assertGreater(p.stat().st_size, 400, name)

    def test_limits_is_honest_about_what_is_missing(self):
        text = (ROOT / "GUIDE-LIMITS.md").read_text(encoding="utf-8")
        for claim in ("No server", "No accounts", "No encryption"):
            self.assertIn(claim, text)

    def test_licensing_names_both_editions(self):
        text = (ROOT / "GUIDE-LICENSING.md").read_text(encoding="utf-8")
        self.assertIn("Personal", text)
        self.assertIn("Commercial", text)
        self.assertIn("PolyForm", text)


if __name__ == "__main__":
    unittest.main()
