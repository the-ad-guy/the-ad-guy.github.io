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


if __name__ == "__main__":
    unittest.main()
