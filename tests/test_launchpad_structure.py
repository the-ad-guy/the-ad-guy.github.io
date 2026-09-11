from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

from playwright.sync_api import sync_playwright


PAGE = Path(__file__).resolve().parents[1] / "production" / "launchpad" / "index.html"


def css_declarations(page_text, selector):
    style = re.search(r"<style>(.*?)</style>", page_text, re.DOTALL).group(1)
    matches = re.findall(re.escape(selector) + r"{([^}]*)}", style)
    return [
        dict(
            declaration.split(":", 1)
            for declaration in block.split(";")
            if ":" in declaration
        )
        for block in matches
    ]


class MainSectionParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.main_depth = 0
        self.section_depth = 0
        self.section_ids = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "main":
            self.main_depth += 1
            return
        if self.main_depth and tag == "section":
            self.section_depth += 1
            if self.section_depth == 1:
                self.section_ids.append(attributes.get("id"))

    def handle_endtag(self, tag):
        if tag == "section" and self.main_depth:
            self.section_depth -= 1
        elif tag == "main":
            self.main_depth -= 1


class TestimonyParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_testimony = False
        self.testimony_depth = 0
        self.has_standard_eyebrow = False
        self.reference_cards = 0
        self.tel_links = []
        self.mailto_links = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = set(attributes.get("class", "").split())

        if tag == "section" and attributes.get("id") == "testimony":
            self.in_testimony = True
            self.testimony_depth = 1
            return

        if not self.in_testimony:
            return

        if tag == "section":
            self.testimony_depth += 1
        elif tag == "p" and {"eyebrow", "violet"}.issubset(classes):
            self.has_standard_eyebrow = True
        elif tag == "article" and "reference-card" in classes:
            self.reference_cards += 1
        elif tag == "a":
            href = attributes.get("href", "")
            if href.startswith("tel:"):
                self.tel_links.append(href)
            elif href.startswith("mailto:"):
                self.mailto_links.append(href)

    def handle_endtag(self, tag):
        if self.in_testimony and tag == "section":
            self.testimony_depth -= 1
            if self.testimony_depth == 0:
                self.in_testimony = False


class MobileControlsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_case_select = False
        self.in_case_option = False
        self.case_options = []
        self.case_labels = []
        self.current_case_label = []
        self.stage_items = []
        self.current_stage = None
        self.stage_item_depth = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = set(attributes.get("class", "").split())

        if tag == "select" and "data-case-select" in attributes:
            self.in_case_select = True
        elif self.in_case_select and tag == "option":
            self.case_options.append(attributes.get("value"))
            self.in_case_option = True
            self.current_case_label = []

        if tag == "div" and "stage-item" in classes:
            self.current_stage = {"button": None, "panel": None}
            self.stage_items.append(self.current_stage)
            self.stage_item_depth = 1
        elif self.current_stage:
            if tag == "div":
                self.stage_item_depth += 1
            if tag == "button" and "data-stage" in attributes:
                self.current_stage["button"] = (
                    attributes.get("data-stage"),
                    attributes.get("aria-expanded"),
                )
            elif tag == "article" and "data-stage-panel" in attributes:
                self.current_stage["panel"] = attributes.get("data-stage-panel")

    def handle_endtag(self, tag):
        if tag == "option" and self.in_case_option:
            self.case_labels.append("".join(self.current_case_label).strip())
            self.in_case_option = False
        elif tag == "select":
            self.in_case_select = False
        elif tag == "div" and self.current_stage:
            self.stage_item_depth -= 1
            if self.stage_item_depth == 0:
                self.current_stage = None

    def handle_data(self, data):
        if self.in_case_option:
            self.current_case_label.append(data)


class LaunchpadStructureTest(unittest.TestCase):
    def test_customer_journey_flows_directly_to_why_launchpad(self):
        parser = MainSectionParser()
        parser.feed(PAGE.read_text(encoding="utf-8"))

        journey_index = parser.section_ids.index("bowtie-funnel")
        self.assertEqual(
            parser.section_ids[journey_index + 1],
            "why-launchpad",
            "The removed planning section still interrupts the journey-to-close flow.",
        )

    def test_testimony_is_the_final_section_after_why_launchpad(self):
        parser = MainSectionParser()
        parser.feed(PAGE.read_text(encoding="utf-8"))

        self.assertEqual(
            parser.section_ids[-2:],
            ["why-launchpad", "testimony"],
            "The testimony section must close the presentation after Why Launchpad.",
        )

    def test_testimony_uses_the_standard_section_header(self):
        parser = TestimonyParser()
        parser.feed(PAGE.read_text(encoding="utf-8"))

        self.assertTrue(
            parser.has_standard_eyebrow,
            "The testimony heading must use the same eyebrow treatment as other sections.",
        )

    def test_references_render_as_clickable_contact_cards(self):
        parser = TestimonyParser()
        parser.feed(PAGE.read_text(encoding="utf-8"))

        self.assertEqual(parser.reference_cards, 4)
        self.assertEqual(len(parser.tel_links), 4)
        self.assertEqual(len(parser.mailto_links), 4)

    def test_mobile_case_picker_offers_every_case_study(self):
        parser = MobileControlsParser()
        parser.feed(PAGE.read_text(encoding="utf-8"))

        self.assertEqual(
            parser.case_options,
            [
                "payments",
                "ai-saas",
                "archiving",
                "mobile",
                "commerce",
                "manufacturing",
                "data",
                "organic",
                "integration",
            ],
        )

    def test_journey_accordion_pairs_every_title_with_its_panel(self):
        parser = MobileControlsParser()
        parser.feed(PAGE.read_text(encoding="utf-8"))

        self.assertEqual(len(parser.stage_items), 5)
        for item in parser.stage_items:
            self.assertEqual(item["button"][0], item["panel"])

        self.assertEqual(
            [item["button"][1] for item in parser.stage_items],
            ["true", "false", "false", "false", "false"],
        )


    def test_dropdown_chevron_is_vertically_centered_in_the_field(self):
        page_text = PAGE.read_text(encoding="utf-8")
        control = css_declarations(page_text, ".case-select-control")[-1]
        chevron = css_declarations(page_text, ".case-select-control:after")[-1]

        self.assertEqual(control.get("min-height"), "72px")
        self.assertEqual(chevron.get("top"), "50%")
        self.assertIn("translateY", chevron.get("transform", ""))

    def test_mobile_accordion_triggers_use_the_full_available_width(self):
        page_text = PAGE.read_text(encoding="utf-8")
        mobile_trigger = css_declarations(page_text, ".enhanced .stage-button")[-1]

        self.assertEqual(mobile_trigger.get("width"), "100%")

class LaunchpadBrowserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def test_mobile_case_picker_preserves_and_updates_both_text_lines(self):
        page = self.browser.new_page(viewport={"width": 390, "height": 844})
        page.goto(PAGE.as_uri())

        title = page.locator(".case-select-display strong")
        descriptor = page.locator(".case-select-display small")
        self.assertEqual(title.count(), 1)
        self.assertEqual(descriptor.count(), 1)
        self.assertEqual(title.text_content(), "Omnichannel growth")
        self.assertEqual(descriptor.text_content(), "Enterprise payments")

        page.locator("[data-case-select]").select_option("integration")
        self.assertEqual(title.text_content(), "Python, APIs & automation")
        self.assertEqual(descriptor.text_content(), "Custom CRM integration")

        picker_box = page.locator(".case-select-control").bounding_box()
        wrap_box = page.locator(".case-select-wrap").bounding_box()
        self.assertGreaterEqual(picker_box["height"], 70)
        self.assertAlmostEqual(picker_box["width"], wrap_box["width"], delta=1)

        title_style = title.evaluate(
            "element => ({fontSize: getComputedStyle(element).fontSize, fontWeight: getComputedStyle(element).fontWeight})"
        )
        descriptor_style = descriptor.evaluate(
            "element => ({fontSize: getComputedStyle(element).fontSize})"
        )
        self.assertEqual(title_style, {"fontSize": "13px", "fontWeight": "600"})
        self.assertEqual(descriptor_style, {"fontSize": "11px"})
        page.close()

    def test_anchor_scroll_animates_when_css_smooth_scrolling_is_unavailable(self):
        page = self.browser.new_page(viewport={"width": 1280, "height": 720})
        page.goto(PAGE.as_uri())
        page.add_style_tag(content="html{scroll-behavior:auto!important}")
        destination = page.evaluate(
            """() => {
                const nav = document.querySelector('.section-nav');
                const heading = document.querySelector('#testimony .section-head');
                return window.scrollY + heading.getBoundingClientRect().top
                    - nav.getBoundingClientRect().height - 24;
            }"""
        )

        page.locator('.section-nav a[href="#testimony"]').click()
        page.wait_for_timeout(80)
        intermediate = page.evaluate("window.scrollY")
        self.assertGreater(intermediate, 0)
        self.assertLess(intermediate, destination - 50)

        page.wait_for_timeout(900)
        self.assertAlmostEqual(page.evaluate("window.scrollY"), destination, delta=2)
        page.close()

if __name__ == "__main__":
    unittest.main()
