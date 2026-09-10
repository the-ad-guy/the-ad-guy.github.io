from html.parser import HTMLParser
from pathlib import Path
import unittest


PAGE = Path(__file__).resolve().parents[1] / "production" / "launchpad" / "index.html"


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


if __name__ == "__main__":
    unittest.main()
