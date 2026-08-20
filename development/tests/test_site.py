from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[2]
PRODUCTION = ROOT / "production"
PAGES = {
    "/": PRODUCTION / "index.html",
    "/projects/": PRODUCTION / "projects" / "index.html",
    "/resume/": PRODUCTION / "resume" / "index.html",
}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.attrs = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrs.append((tag, dict(attrs)))


def local_target(url):
    parsed = urlparse(url)
    if parsed.scheme or parsed.netloc or not parsed.path.startswith("/"):
        return None
    if parsed.path.endswith("/"):
        return PRODUCTION / parsed.path.lstrip("/") / "index.html"
    return PRODUCTION / parsed.path.lstrip("/")


class PortfolioSiteTests(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            *PAGES.values(),
            PRODUCTION / "assets/css/styles.css",
            PRODUCTION / "assets/js/main.js",
            PRODUCTION / "assets/images/tim-gibson-headshot.webp",
            PRODUCTION / "assets/documents/tim-gibson-resume.pdf",
            PRODUCTION / "favicon.ico",
            PRODUCTION / "assets/images/favicon-32x32.png",
            PRODUCTION / "assets/images/favicon-16x16.png",
            PRODUCTION / "assets/images/apple-touch-icon.png",
            PRODUCTION / "CNAME",
            PRODUCTION / "robots.txt",
            PRODUCTION / "sitemap.xml",
            PRODUCTION / "404.html",
        ]
        for path in required:
            with self.subTest(path=path):
                self.assertTrue(path.is_file(), path)

    def test_page_structure_metadata_and_links(self):
        titles = set()
        descriptions = set()
        for route, path in PAGES.items():
            with self.subTest(route=route):
                source = path.read_text(encoding="utf-8")
                parser = PageParser()
                parser.feed(source)
                attrs = parser.attrs
                title = source.split("<title>", 1)[1].split("</title>", 1)[0].strip()
                description = next(
                    a["content"]
                    for tag, a in attrs
                    if tag == "meta" and a.get("name") == "description"
                )
                self.assertEqual(parser.tags.count("h1"), 1)
                self.assertTrue(
                    any(tag == "link" and a.get("rel") == "canonical" for tag, a in attrs)
                )
                self.assertTrue(
                    any(tag == "meta" and a.get("property") == "og:title" for tag, a in attrs)
                )
                self.assertTrue(
                    any(tag == "a" and "skip-link" in a.get("class", "").split() for tag, a in attrs)
                )
                self.assertNotIn("\u2014", source)
                for destination in PAGES:
                    self.assertTrue(
                        any(tag == "a" and a.get("href") == destination for tag, a in attrs),
                        destination,
                    )
                for tag, a in attrs:
                    url = a.get("href") if tag in {"a", "link"} else a.get("src")
                    target = local_target(url or "")
                    if target:
                        self.assertTrue(target.exists(), (route, url))
                titles.add(title)
                descriptions.add(description)
        self.assertEqual(len(titles), len(PAGES))
        self.assertEqual(len(descriptions), len(PAGES))

    def test_external_links_are_safe(self):
        for path in PAGES.values():
            parser = PageParser()
            parser.feed(path.read_text(encoding="utf-8"))
            for tag, attrs in parser.attrs:
                if tag == "a" and attrs.get("target") == "_blank":
                    rel = set(attrs.get("rel", "").split())
                    self.assertTrue({"noopener", "noreferrer"}.issubset(rel), attrs)

    def test_deployment_assets(self):
        self.assertEqual(
            (PRODUCTION / "CNAME").read_text(encoding="utf-8").strip(),
            "theadguy.org",
        )
        self.assertEqual(
            (PRODUCTION / "assets/documents/tim-gibson-resume.pdf").read_bytes()[:4],
            b"%PDF",
        )
        image = (PRODUCTION / "assets/images/tim-gibson-headshot.webp").read_bytes()
        self.assertEqual(image[:4], b"RIFF")
        self.assertEqual(image[8:12], b"WEBP")

    def test_dark_cta_secondary_button_has_readable_contrast(self):
        css = (PRODUCTION / "assets/css/styles.css").read_text(encoding="utf-8")
        selector = ".cta-panel .button-secondary {"
        self.assertIn(selector, css)
        rule = css.split(selector, 1)[1].split("}", 1)[0]
        self.assertIn("color: var(--white);", rule)
        self.assertIn("border-color: rgba(255, 255, 255, 0.72);", rule)

    def test_contact_details_are_current(self):
        linkedin = "https://www.linkedin.com/in/tim77/"
        for path in [*PAGES.values(), PRODUCTION / "404.html"]:
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertNotIn("timjgibl@gmail.com", source)
                self.assertIn("mailto:timjgib@gmail.com", source)
                self.assertIn(linkedin, source)

    def test_marketing_engineering_line_includes_crm_reporting(self):
        source = (PRODUCTION / "resume" / "index.html").read_text(encoding="utf-8")
        expected = (
            "Marketing Engineering:</strong> Google Ads Scripts | Google Ads API | "
            "Google Apps Script | JavaScript | SQL/BigQuery | Python | HTML/CSS | "
            "Zapier | CRM Integrations &amp; Reporting (HubSpot, Salesforce, Odoo, and "
            "additional platforms)"
        )
        self.assertIn(expected, source)

    def test_google_tag_manager_is_installed_on_every_page(self):
        container = "GTM-58H5MRH7"
        for path in [*PAGES.values(), PRODUCTION / "404.html"]:
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                head = source.split("</head>", 1)[0]
                self.assertIn("googletagmanager.com/gtm.js", head)
                self.assertIn(container, head)
                body = source.split("<body>", 1)[1]
                self.assertIn(
                    f"https://www.googletagmanager.com/ns.html?id={container}",
                    body,
                )

    def test_required_production_files_are_tracked(self):
        required = [
            "production/index.html",
            "production/projects/index.html",
            "production/resume/index.html",
            "production/assets/css/styles.css",
            "production/assets/js/main.js",
            "production/assets/images/tim-gibson-headshot.webp",
            "production/assets/documents/tim-gibson-resume.pdf",
            "production/favicon.ico",
            "production/assets/images/favicon-32x32.png",
            "production/assets/images/favicon-16x16.png",
            "production/assets/images/apple-touch-icon.png",
        ]
        for path in required:
            with self.subTest(path=path):
                result = subprocess.run(
                    ["git", "ls-files", "--error-unmatch", path],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_cta_panel_content_is_centered(self):
        css = (PRODUCTION / "assets/css/styles.css").read_text(encoding="utf-8")
        selector = ".cta-panel {"
        self.assertIn(selector, css)
        rule = css.split(selector, 1)[1].split("}", 1)[0]
        self.assertIn("text-align: center;", rule)
        self.assertIn(".cta-panel .button-row {", css)
        button_row_rule = css.split(".cta-panel .button-row {", 1)[1].split("}", 1)[0]
        self.assertIn("justify-content: center;", button_row_rule)


if __name__ == "__main__":
    unittest.main()
