"""Tests for quiz (an answer model) and gallery (image metadata)."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _extract as extract      # noqa: E402
from kiln import catalog as cat  # noqa: E402
from kiln import guards          # noqa: E402
from kiln import spec as specmod  # noqa: E402
from kiln import verify          # noqa: E402

CEILING = 100 * 1024
QUIZ = ROOT / "specs" / "gallery" / "quiz.md"
GAL = ROOT / "specs" / "gallery" / "gallery.md"


def run_js(src: str) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
        f.write(src)
        path = f.name
    try:
        return subprocess.run(["node", path], capture_output=True, text=True)
    finally:
        Path(path).unlink(missing_ok=True)


class TestScore(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def case(self, questions, picks, want):
        src = extract.source("scoreOf") + (
            "const got = scoreOf(%s, %s, 'answer');\n"
            "if (got !== %s) { console.log('FAIL ' + got); process.exit(1); }\n"
            "console.log('PASS');\n"
            % (json.dumps(questions), json.dumps(picks), json.dumps(want)))
        p = run_js(src)
        self.assertEqual(0, p.returncode, p.stdout + p.stderr)

    def test_two_of_three(self):
        qs = [{"answer": "Sulphur"}, {"answer": "Pulsatilla"}, {"answer": "Bryonia"}]
        self.case(qs, ["Sulphur", "Nux vomica", "Bryonia"], 2)

    def test_all_wrong(self):
        self.case([{"answer": "A"}, {"answer": "B"}], ["C", "D"], 0)

    def test_case_and_space_are_forgiven(self):
        self.case([{"answer": "Sulphur"}], ["  sulphur "], 1)

    def test_an_unanswered_question_is_not_right(self):
        self.case([{"answer": "A"}], [], 0)

    def test_an_empty_answer_is_never_right(self):
        self.case([{"answer": ""}], [""], 0)

    def test_no_questions_is_zero(self):
        self.case([], [], 0)


class TestQuizSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_names_its_answer_field(self):
        s = specmod.load(QUIZ, self.c)
        self.assertEqual("answer", s["quiz"]["answer"])

    def test_an_answer_on_a_tags_field_is_refused(self):
        s = specmod.load(QUIZ, self.c)
        s["quiz"]["answer"] = "options"
        problems = specmod.validate(s, self.c, "quiz.md")
        self.assertTrue(any("text or select" in p for p in problems), problems)

    def test_a_quiz_with_no_tags_field_is_refused(self):
        s = specmod.load(QUIZ, self.c)
        s["entities"][0]["fields"] = [f for f in s["entities"][0]["fields"]
                                      if f["type"] != "tags"]
        problems = specmod.validate(s, self.c, "quiz.md")
        self.assertTrue(any("tags field" in p for p in problems), problems)

    def test_it_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(QUIZ, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function renderQuiz(", html)
            self.assertIn("function scoreOf(", html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)


class TestGallerySpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_names_its_image_field(self):
        s = specmod.load(GAL, self.c)
        self.assertEqual("image", s["gallery"]["image"])

    def test_an_image_field_of_type_text_is_refused(self):
        s = specmod.load(GAL, self.c)
        s["gallery"]["image"] = "title"
        problems = specmod.validate(s, self.c, "gallery.md")
        self.assertTrue(any("must be an image field" in p for p in problems), problems)

    def test_it_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(GAL, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function renderGallery(", html)
            self.assertIn('loading = "lazy"', html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)

    def test_a_gallery_carries_no_quiz(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            verify.build_and_check(GAL, self.c, out)
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("function renderQuiz(", html)
            self.assertNotIn("quizState", html)


class TestBlockOwnership(unittest.TestCase):
    """C18: the guard that stops a name escaping its capability block."""

    def setUp(self):
        self.c = cat.load()

    def test_the_template_is_clean(self):
        bad = [r.name + " " + r.detail for r in guards.check_block_ownership(self.c)
               if not r.ok]
        self.assertEqual([], bad)

    def test_it_catches_a_name_in_the_wrong_block(self):
        import kiln.guards as g
        src = (
            "/* @only alpha */\n"
            "let shared = 1;\n"
            "/* @end only */\n"
            "/* @only beta */\n"
            "function useIt() { return shared + 1; }\n"
            "/* @end only */\n"
        )
        real = (g.ROOT / "templates" / "app" / "index.html")
        backup = real.read_text(encoding="utf-8")
        try:
            real.write_text(src, encoding="utf-8")
            rows = g.check_block_ownership(self.c)
            self.assertTrue(any(not r.ok for r in rows), "the escape was not caught")
        finally:
            real.write_text(backup, encoding="utf-8")

    def test_typeof_and_property_access_are_not_escapes(self):
        import kiln.guards as g
        src = (
            "/* @only alpha */\n"
            "function probe() { return 1; }\n"
            "/* @end only */\n"
            "/* @only beta */\n"
            "const a = typeof probe !== 'undefined' ? probe() : 0;\n"
            "const b = MODEL.alpha.probe;\n"
            "/* @end only */\n"
        )
        real = (g.ROOT / "templates" / "app" / "index.html")
        backup = real.read_text(encoding="utf-8")
        try:
            real.write_text(src, encoding="utf-8")
            rows = g.check_block_ownership(self.c)
            self.assertFalse([r for r in rows if not r.ok], [r.detail for r in rows])
        finally:
            real.write_text(backup, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
