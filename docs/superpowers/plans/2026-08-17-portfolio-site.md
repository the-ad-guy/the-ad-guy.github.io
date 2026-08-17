# Tim Gibson Portfolio Website Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish a responsive three-page professional portfolio for Tim Gibson using GitHub Pages and the custom domain `theadguy.org`.

**Architecture:** The deployable site lives entirely in `production/` as semantic HTML, one shared CSS file, and one small progressive-enhancement JavaScript file. GitHub Actions uploads only `production/` as the Pages artifact, while reusable validation and local-working files stay in `development/`.

**Tech Stack:** HTML5, CSS3, vanilla JavaScript, Python standard library tests, GitHub Actions, GitHub Pages

**Spec:** `docs/superpowers/specs/2026-08-17-portfolio-site-design.md`

## Global Constraints

- The site has exactly three primary destinations: Home, Projects, and Resume.
- Production code and public assets live only under `production/`.
- Use no site framework, package manager, Jekyll theme, database, contact form, analytics tracker, or cookie-consent interface.
- Use no em dashes in public copy.
- Use the supplied headshot as an optimized WebP image.
- Provide a downloadable PDF generated from Tim's latest resume.
- Publish with GitHub Actions using GitHub's built-in repository token.
- Verify the default GitHub Pages URL before connecting `theadguy.org`.
- Meet WCAG AA color-contrast targets and provide keyboard-visible focus styles.

---

## File Map

- `production/index.html`: Homepage content and homepage-specific metadata.
- `production/projects/index.html`: Complete project portfolio and project links.
- `production/resume/index.html`: Accessible HTML resume and PDF download link.
- `production/assets/css/styles.css`: Shared design tokens, layout, components, responsive rules, print rules, and interaction states.
- `production/assets/js/main.js`: Accessible mobile-navigation enhancement and automatic footer year.
- `production/assets/images/tim-gibson-headshot.webp`: Cropped and compressed production headshot.
- `production/assets/documents/tim-gibson-resume.pdf`: Downloadable resume.
- `production/CNAME`: GitHub Pages custom-domain declaration.
- `production/robots.txt`: Search crawler policy and sitemap location.
- `production/sitemap.xml`: Canonical URLs for all three pages.
- `production/404.html`: Branded recovery page with navigation back to the site.
- `development/tests/test_site.py`: Dependency-free structural, metadata, asset, link, and content-policy tests.
- `.github/workflows/deploy-pages.yml`: GitHub Pages build and deployment workflow.
- `.gitignore`: Local and generated development exclusions.
- `README.md`: Maintenance, local preview, validation, and deployment guidance.

---

### Task 1: Validation Contract and Production Assets

**Files:**
- Create: `development/tests/test_site.py`
- Create: `production/assets/images/tim-gibson-headshot.webp`
- Create: `production/assets/documents/tim-gibson-resume.pdf`
- Source: `images/full headshot.jpg`
- Source: `C:/Users/Tim/Downloads/Tim Gibson Resume.docx`

**Interfaces:**
- Consumes: The approved design specification, source headshot, and latest resume.
- Produces: A test command used by every later task and two public asset paths referenced by HTML.

- [ ] **Step 1: Create the failing site contract test**

Create a standard-library `unittest` suite that asserts the required production files exist, every page has one `h1`, unique title and description metadata, canonical and Open Graph metadata, a skip link, the three navigation destinations, no em dash characters, and no broken root-relative asset references. It must also assert that `CNAME` equals `theadguy.org`, the PDF begins with `%PDF`, and the image has a WebP `RIFF` header.

```python
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
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
        self.text = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrs.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


def local_target(url):
    parsed = urlparse(url)
    if parsed.scheme or parsed.netloc or not parsed.path.startswith("/"):
        return None
    path = parsed.path
    if path.endswith("/"):
        return PRODUCTION / path.lstrip("/") / "index.html"
    return PRODUCTION / path.lstrip("/")


class PortfolioSiteTests(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            *PAGES.values(),
            PRODUCTION / "assets/css/styles.css",
            PRODUCTION / "assets/js/main.js",
            PRODUCTION / "assets/images/tim-gibson-headshot.webp",
            PRODUCTION / "assets/documents/tim-gibson-resume.pdf",
            PRODUCTION / "CNAME",
            PRODUCTION / "robots.txt",
            PRODUCTION / "sitemap.xml",
            PRODUCTION / "404.html",
        ]
        for path in required:
            self.assertTrue(path.is_file(), path)

    def test_page_structure_metadata_and_links(self):
        titles = set()
        descriptions = set()
        for route, path in PAGES.items():
            parser = PageParser()
            source = path.read_text(encoding="utf-8")
            parser.feed(source)
            attrs = parser.attrs
            title = source.split("<title>", 1)[1].split("</title>", 1)[0].strip()
            description = next(a["content"] for tag, a in attrs if tag == "meta" and a.get("name") == "description")
            self.assertEqual(parser.tags.count("h1"), 1, route)
            self.assertTrue(any(tag == "link" and a.get("rel") == "canonical" for tag, a in attrs), route)
            self.assertTrue(any(tag == "meta" and a.get("property") == "og:title" for tag, a in attrs), route)
            self.assertTrue(any(tag == "a" and a.get("class") == "skip-link" for tag, a in attrs), route)
            self.assertNotIn("\u2014", source, route)
            for destination in PAGES:
                self.assertTrue(any(tag == "a" and a.get("href") == destination for tag, a in attrs), (route, destination))
            for tag, a in attrs:
                url = a.get("href") if tag in {"a", "link"} else a.get("src")
                target = local_target(url or "")
                if target:
                    self.assertTrue(target.exists(), (route, url))
            titles.add(title)
            descriptions.add(description)
        self.assertEqual(len(titles), len(PAGES))
        self.assertEqual(len(descriptions), len(PAGES))

    def test_deployment_assets(self):
        self.assertEqual((PRODUCTION / "CNAME").read_text(encoding="utf-8").strip(), "theadguy.org")
        self.assertEqual((PRODUCTION / "assets/documents/tim-gibson-resume.pdf").read_bytes()[:4], b"%PDF")
        image = (PRODUCTION / "assets/images/tim-gibson-headshot.webp").read_bytes()
        self.assertEqual(image[:4], b"RIFF")
        self.assertEqual(image[8:12], b"WEBP")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the contract test and confirm it fails**

Run: `python -m unittest development.tests.test_site -v`

Expected: FAIL because the production pages and public assets do not exist yet.

- [ ] **Step 3: Prepare the production headshot**

Crop the 2048 by 1365 source image to a balanced portrait composition, resize it to a maximum rendered density near 900 pixels on the long edge, remove unnecessary metadata, and save it as `production/assets/images/tim-gibson-headshot.webp`. Confirm Tim's face remains sharp and naturally framed.

- [ ] **Step 4: Generate and verify the resume PDF**

Render `C:/Users/Tim/Downloads/Tim Gibson Resume.docx` to PDF, save it as `production/assets/documents/tim-gibson-resume.pdf`, render the PDF pages to images, and visually confirm that text, bullets, spacing, links, and both pages remain intact.

- [ ] **Step 5: Commit the validation contract and assets**

```powershell
git add development/tests/test_site.py production/assets
git commit -m "test: define portfolio contract and add assets"
```

---

### Task 2: Shared Design System and Page Shell

**Files:**
- Create: `production/assets/css/styles.css`
- Create: `production/assets/js/main.js`
- Create: `production/index.html`
- Create: `production/projects/index.html`
- Create: `production/resume/index.html`

**Interfaces:**
- Consumes: `/assets/images/tim-gibson-headshot.webp` and `/assets/documents/tim-gibson-resume.pdf`.
- Produces: Shared classes for `.site-header`, `.site-nav`, `.button`, `.section`, `.card`, `.eyebrow`, `.metric`, `.site-footer`, and the `[data-menu-button]` navigation contract.

- [ ] **Step 1: Add minimal semantic page shells**

Create all three HTML documents with `lang="en"`, viewport metadata, unique titles and descriptions, canonical URLs, Open Graph metadata, a skip link, shared header navigation, an empty but labelled `main`, shared footer, root-relative CSS and JavaScript references, and the correct `aria-current="page"` navigation item.

- [ ] **Step 2: Run the contract test and inspect remaining failures**

Run: `python -m unittest development.tests.test_site -v`

Expected: Page structure checks pass. Missing supporting files and incomplete public content remain to be implemented.

- [ ] **Step 3: Implement the shared visual system**

Define navy, blue, warm white, white, gray, border, and focus-ring custom properties. Add a modern system-font stack, fluid type sizes with `clamp()`, a centered content container, responsive grid utilities, subtle cards, restrained shadows, buttons, accessible focus states, a sticky translucent header, mobile navigation, reduced-motion handling, and print styles for the resume page.

- [ ] **Step 4: Implement progressive navigation behavior**

Use a single `DOMContentLoaded` handler that toggles `aria-expanded` and the mobile menu's open state, closes the menu after a navigation selection, closes it with Escape, and writes the current year into `[data-current-year]`. The navigation links must remain present and usable without JavaScript.

- [ ] **Step 5: Verify responsive source rules**

Run: `rg -n "@media|prefers-reduced-motion|focus-visible|data-menu-button" production/assets production/*.html production/projects/index.html production/resume/index.html`

Expected: Output includes narrow-screen navigation, wide-screen layout, reduced-motion, keyboard focus, and the menu hook.

- [ ] **Step 6: Commit the shared shell**

```powershell
git add production/index.html production/projects/index.html production/resume/index.html production/assets/css/styles.css production/assets/js/main.js
git commit -m "feat: add portfolio design system and page shell"
```

---

### Task 3: Homepage Content

**Files:**
- Modify: `production/index.html`

**Interfaces:**
- Consumes: Shared design classes, headshot asset, public project routes, and resume route.
- Produces: The site's primary positioning, featured results, specialties, and calls to action.

- [ ] **Step 1: Add the homepage hero**

Use the primary positioning `Paid Media Strategy, Analytics & Marketing Automation`. Introduce Tim as a paid media leader who connects campaign execution, measurement, CRM data, and automation to business outcomes. Pair the copy with the headshot and include `View Projects` and `View Resume` actions.

- [ ] **Step 2: Add specialties and quantified results**

Create three specialty blocks for paid media leadership, analytics and measurement, and automation. Present selected outcomes accurately: 69% higher paid-media-attributed revenue, 34% more opportunities, 25% higher ROAS, 119% higher pipeline value, 72% higher closed revenue, and at least 52 hours of annual reporting work saved. Label client results as selected examples and avoid implying that every figure came from one engagement.

- [ ] **Step 3: Add featured projects and contact path**

Feature Ads Notes, Global Consent Manager, and Google Ads Automations with concise problem-and-value summaries. End with a professional invitation to connect through Tim's email and LinkedIn profile, using the contact details verified from the source resume.

- [ ] **Step 4: Run the contract test**

Run: `python -m unittest development.tests.test_site -v`

Expected: PASS for homepage structure, metadata, internal references, and copy policy.

- [ ] **Step 5: Commit the homepage**

```powershell
git add production/index.html
git commit -m "feat: build portfolio homepage"
```

---

### Task 4: Projects Portfolio

**Files:**
- Modify: `production/projects/index.html`

**Interfaces:**
- Consumes: Shared card, tag, link, and section classes.
- Produces: A complete projects portfolio with external links to public work.

- [ ] **Step 1: Add the project-page introduction**

Explain that the projects combine paid media expertise, analytics, AI-assisted coding, and workflow automation to solve practical marketing problems.

- [ ] **Step 2: Add six project entries**

For each project, include the approved title, tools, problem solved, functionality, and outcome. Use these public links where applicable:

```text
Ads Notes: https://chromewebstore.google.com/detail/ads-notes/nindafjblmbdjhmjkjcmfklcddkkjegj
Global Consent Manager: https://github.com/the-ad-guy/global-consent-manager
GitHub profile: https://github.com/the-ad-guy
```

Describe proprietary projects without exposing client names, credentials, source code, or confidential implementation details.

- [ ] **Step 3: Add safe external-link behavior**

Every link using `target="_blank"` must also use `rel="noopener noreferrer"` and include accessible context indicating that it opens an external destination.

- [ ] **Step 4: Run tests and scan project links**

Run: `python -m unittest development.tests.test_site -v`

Run: `rg -n "chromewebstore.google.com|github.com/the-ad-guy|noopener noreferrer" production/projects/index.html`

Expected: Tests pass and all public destinations appear with safe link attributes.

- [ ] **Step 5: Commit the projects page**

```powershell
git add production/projects/index.html
git commit -m "feat: add technical project portfolio"
```

---

### Task 5: Web Resume

**Files:**
- Modify: `production/resume/index.html`

**Interfaces:**
- Consumes: The latest resume document, shared typography and layout classes, and the downloadable PDF asset.
- Produces: A recruiter-readable HTML resume and `/assets/documents/tim-gibson-resume.pdf` download action.

- [ ] **Step 1: Transcribe and structure the resume content**

Use semantic sections for relevant work experience, additional experience, selected projects, technical skills, education, and certifications. Preserve employer names, role names, date ranges, performance metrics, platform counts, and qualification wording from the latest source resume.

- [ ] **Step 2: Adapt formatting for web readability**

Use headings, role groups, compact metadata rows, concise bullet lists, and a desktop-friendly measure. Keep chronological order and make concurrent roles at Vital and the part-time Dog Nanny role clear.

- [ ] **Step 3: Add resume actions**

Place a `Download PDF` button near the page introduction and a `Print Resume` button that calls `window.print()`. Ensure print CSS removes navigation and buttons while producing a clean document.

- [ ] **Step 4: Compare the HTML version against the source**

Extract text from both the source DOCX and the HTML page, then compare every employer, title, date, metric, certification, platform, technology, and public link. Correct only transcription or web-formatting issues; do not invent new claims.

- [ ] **Step 5: Run the contract test**

Run: `python -m unittest development.tests.test_site -v`

Expected: PASS for resume structure, metadata, assets, internal references, and copy policy.

- [ ] **Step 6: Commit the resume page**

```powershell
git add production/resume/index.html
git commit -m "feat: add web resume and PDF download"
```

---

### Task 6: Search Files, Deployment, and Documentation

**Files:**
- Create: `production/CNAME`
- Create: `production/robots.txt`
- Create: `production/sitemap.xml`
- Create: `production/404.html`
- Create: `.github/workflows/deploy-pages.yml`
- Create: `.gitignore`
- Modify: `README.md`

**Interfaces:**
- Consumes: The completed production site.
- Produces: Search-engine discovery, custom-domain declaration, branded recovery, automated Pages publishing, and maintenance instructions.

- [ ] **Step 1: Add domain and search-discovery files**

Use the exact custom domain in `CNAME`, allow normal crawling in `robots.txt`, point crawlers to `https://theadguy.org/sitemap.xml`, and list the canonical Home, Projects, and Resume URLs in `sitemap.xml`.

- [ ] **Step 2: Add the branded 404 page**

Reuse the production design system and provide direct navigation to Home, Projects, and Resume. Give the page its own title, description, canonical metadata, one `h1`, and helpful recovery copy.

- [ ] **Step 3: Add the GitHub Pages workflow**

Create a workflow triggered by pushes to `main` and manual dispatch. Use `actions/checkout`, `actions/configure-pages`, `actions/upload-pages-artifact` with `path: production`, and `actions/deploy-pages`. Set `pages: write` and `id-token: write` permissions, serialize deployments with a Pages concurrency group, and deploy through the `github-pages` environment.

- [ ] **Step 4: Document maintenance and local verification**

Update the README with the folder map, `python -m http.server 8000 --directory production` preview command, `python -m unittest development.tests.test_site -v` validation command, deployment behavior, and the custom-domain activation sequence. Ignore local caches, temporary exports, editor files, and development drafts that should not be committed.

- [ ] **Step 5: Run the complete automated validation**

Run: `python -m unittest development.tests.test_site -v`

Expected: All tests PASS.

Run: `git diff --check`

Expected: No whitespace errors.

- [ ] **Step 6: Preview all routes locally**

Start `python -m http.server 8000 --directory production`, request `/`, `/projects/`, `/resume/`, `/404.html`, the headshot, stylesheet, JavaScript, and PDF, and confirm every response returns HTTP 200 with the expected content type.

- [ ] **Step 7: Perform visual review**

Review Home, Projects, Resume, and 404 at phone and desktop widths. Confirm there is no overflow, clipped text, missing content, awkward headshot crop, unreadable contrast, broken navigation, or print-only content visible on screen.

- [ ] **Step 8: Commit the deployable site**

```powershell
git add production .github/workflows/deploy-pages.yml .gitignore README.md development/tests/test_site.py
git commit -m "feat: prepare portfolio for GitHub Pages"
```

---

### Task 7: Publish and Verify GitHub Pages

**Files:**
- Verify: Repository branch `main`
- Verify: GitHub Actions workflow run
- Verify: `https://the-ad-guy.github.io`

**Interfaces:**
- Consumes: Committed production artifact and GitHub repository authentication.
- Produces: Public GitHub Pages site ready for custom-domain DNS configuration.

- [ ] **Step 1: Push the completed commits**

Run: `git push origin main`

Expected: The remote `main` branch advances to the completed local commit.

- [ ] **Step 2: Verify the Pages workflow**

Confirm that the GitHub Actions deployment finishes successfully and that the Pages environment reports the deployed URL.

- [ ] **Step 3: Verify the default public site**

Open `https://the-ad-guy.github.io` and verify Home, Projects, Resume, PDF download, headshot, internal navigation, and external project links.

- [ ] **Step 4: Hand off custom-domain configuration**

Provide the exact GitHub Pages setting and DNS records Tim must add for `theadguy.org`. After DNS verification, confirm HTTPS becomes available and instruct Tim to enable `Enforce HTTPS`.

