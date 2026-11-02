import re
from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]


def css_variables(css):
    return dict(re.findall(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{6})\s*;", css))


def resolve_color(css, value):
    variables = css_variables(css)
    var = re.fullmatch(r"var\((--[\w-]+)\)", value.strip())
    color = variables[var.group(1)] if var else value.strip()
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        raise ValueError(f"Unsupported color: {color}")
    return color


def rule_declarations(css, pattern):
    match = re.search(pattern, css)
    if match is None:
        raise ValueError(f"Missing style rule: {pattern}")
    return dict(re.findall(r"(?:^|;)\s*([\w-]+)\s*:\s*([^;]+)", match.group(1)))


def button_colors(css, selector=r"\.primary-button"):
    declarations = rule_declarations(css, selector + r"\s*\{([^}]*)\}")
    return resolve_color(css, declarations["color"]), resolve_color(css, declarations["background"])


def primary_colors(css):
    return button_colors(css)


def hover_colors(css):
    background = rule_declarations(css, r"\.primary-button:hover\s*\{([^}]*)\}")["background"]
    return primary_colors(css)[0], resolve_color(css, background)


def contrast_ratio(first, second):
    def luminance(color):
        channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
        return sum(c * weight for c, weight in zip(linear, (0.2126, 0.7152, 0.0722)))

    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


class LocalReferences(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.add(attributes["id"])
        for name in ("href", "src"):
            if attributes.get(name):
                self.links.append(attributes[name])


class SiteTests(unittest.TestCase):
    def test_page_has_primary_action(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('class="button primary-button"', html)

    def test_primary_action_has_readable_contrast(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        ratio = contrast_ratio(*primary_colors(css))
        self.assertGreaterEqual(ratio, 4.5, "primary button text must reach a 4.5:1 contrast ratio")

    def test_primary_action_hover_stays_readable(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        ratio = contrast_ratio(*hover_colors(css))
        self.assertGreaterEqual(ratio, 4.5, "primary button hover text must reach a 4.5:1 contrast ratio")

    def test_contrast_calculation(self):
        self.assertAlmostEqual(contrast_ratio("#000000", "#ffffff"), 21)
        self.assertEqual(contrast_ratio("#f6f4ee", "#f6f4ee"), 1)

    def test_local_links_and_assets_exist(self):
        page = LocalReferences()
        page.feed((ROOT / "index.html").read_text(encoding="utf-8"))
        for link in page.links:
            with self.subTest(link=link):
                if link.startswith("#"):
                    self.assertIn(link[1:], page.ids)
                elif not re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", link):
                    self.assertFalse(link.startswith("/"), "project Pages needs relative links")
                    self.assertTrue((ROOT / link).exists())


if __name__ == "__main__":
    unittest.main()
