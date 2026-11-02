"""Guards for the page's opt-in motion layer.

The page animates with CSS only, so it must keep working without
JavaScript, and the motion must stay behind
``prefers-reduced-motion: no-preference`` so motion-sensitive visitors
receive the plain static page.
"""

import re
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]
GATE = "@media (prefers-reduced-motion: no-preference)"


def block_body(css, header):
    """Return the text inside the first rule block opened by ``header``."""
    start = css.index(header)
    opening = css.index("{", start)
    depth = 0
    for index in range(opening, len(css)):
        if css[index] == "{":
            depth += 1
        elif css[index] == "}":
            depth -= 1
            if depth == 0:
                return opening + 1, index
    raise AssertionError(f"unterminated block for {header}")


class MotionTests(unittest.TestCase):
    def setUp(self):
        self.css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.html = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_motion_is_opt_in_for_reduced_motion(self):
        start, end = block_body(self.css, GATE)
        for match in re.finditer(r"(?:^|[;{\s])animation(?:-name)?\s*:", self.css):
            with self.subTest(position=match.start()):
                self.assertTrue(
                    start <= match.start() < end,
                    "every animation must sit inside the reduced-motion gate",
                )

    def test_reduced_motion_disables_smooth_scrolling(self):
        start, end = block_body(self.css, "@media (prefers-reduced-motion: reduce)")
        self.assertIn("scroll-behavior: auto", self.css[start:end])

    def test_referenced_keyframes_are_defined(self):
        defined = set(re.findall(r"@keyframes\s+([\w-]+)", self.css))
        referenced = set()
        for value in re.findall(r"animation(?:-name)?\s*:\s*([^;}]+)", self.css):
            for token in re.split(r"[,]", value):
                name = token.split()[0]
                if re.fullmatch(r"[a-zA-Z][\w-]*", name) and name not in {
                    "none", "linear", "ease", "ease-in", "ease-out", "ease-in-out",
                    "infinite", "both", "forwards", "backwards", "normal", "alternate",
                }:
                    referenced.add(name)
        self.assertEqual(referenced - defined, set(), "undefined animation names")

    def test_motion_needs_no_javascript(self):
        self.assertNotIn("<script", self.html.lower())
        self.assertNotRegex(self.html, r"\.js\b")


if __name__ == "__main__":
    unittest.main()
