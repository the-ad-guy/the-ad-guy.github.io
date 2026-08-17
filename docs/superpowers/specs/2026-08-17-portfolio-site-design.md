# Tim Gibson Portfolio Website Design

## Purpose

Build a fast, polished professional portfolio for Tim Gibson at `theadguy.org`. The site will position Tim for paid digital advertising, paid media strategy, marketing analytics, measurement, and automation roles. It will give recruiters and hiring managers a concise overview, evidence of business impact, access to selected technical projects, and a downloadable resume.

## Success Criteria

- The site has three clear destinations: Home, Projects, and Resume.
- Visitors can understand Tim's specialization and strongest differentiators within the first screen.
- The site works cleanly on phones, tablets, and desktop screens.
- The deployed site uses only static HTML, CSS, JavaScript, images, and documents.
- GitHub Pages publishes only files inside `production/`.
- The default GitHub Pages URL works before `theadguy.org` is connected.
- The site is accessible, quick to load, and easy for Tim to maintain without a framework.

## Audience and Positioning

The primary audience is recruiters, hiring managers, and professional contacts evaluating Tim for senior paid media, digital acquisition, analytics, or marketing operations roles.

The primary positioning will combine:

- Paid media strategy and account leadership
- Analytics, attribution, and business-outcome reporting
- Technical implementation and AI-assisted automation
- Cross-functional collaboration across advertising, CRM, landing-page, and measurement systems

The tone will be confident, specific, and professional. Copy will avoid inflated claims, generic marketing language, em dashes, and unnecessary technical jargon.

## Information Architecture

### Home

The homepage will contain:

1. A compact header with Tim's name and navigation.
2. A hero section with the optimized headshot, a concise positioning statement, and calls to view projects or the resume.
3. Three specialty areas covering paid media, analytics and measurement, and automation.
4. A results section using selected quantified achievements from Tim's resume.
5. A featured-projects preview linking to the Projects page.
6. A closing contact section and consistent footer.

### Projects

The Projects page will present selected work as structured cards or sections. Each project will include a title, tools, a concise explanation of the problem solved, and the outcome or operational value. Public projects will link to GitHub or the Chrome Web Store where available.

Initial projects:

- Ads Notes Chrome Extension
- Global Consent Manager
- Google Ads Automations
- Google Workspace Automations
- Custom CRM Integrations
- Cross-Platform Budget Pacing Tracker

AI-assisted coding will be mentioned where it adds useful context, without repeating the phrase throughout every project.

### Resume

The Resume page will contain a concise, readable HTML version of Tim's resume and a prominent PDF download. It will preserve the resume's factual content while adapting spacing and hierarchy for the web. The page will cover relevant experience, additional experience, selected projects or technical capabilities, education, certifications, and skills as appropriate to the latest source resume.

## Visual Direction

The design will use a restrained navy, blue, warm white, and muted gray palette aligned with Tim's resume. Strong typography, whitespace, thin rules, subtle card borders, and modest color accents will create the visual identity. The headshot will appear beside the homepage introduction and will not dominate the page.

The design will avoid stock imagery, decorative illustrations, excessive animation, skill meters, carousels, and visual effects that distract from Tim's experience.

## Responsive and Interactive Behavior

- Desktop navigation will appear inline in the header.
- Small screens will use a compact accessible menu controlled by minimal JavaScript.
- Navigation will clearly indicate the current page.
- Cards and result blocks will stack cleanly at narrow widths.
- Links, controls, and focus states will be keyboard accessible.
- Motion will be minimal and will respect reduced-motion preferences.
- The site will remain fully usable if JavaScript is unavailable, except for the optional mobile-menu enhancement.

## Technical Architecture

The deployed site will use semantic static HTML and a shared stylesheet. A small shared JavaScript file will handle only navigation and minor progressive enhancements.

```text
theadguy.org/
├── production/
│   ├── index.html
│   ├── projects/index.html
│   ├── resume/index.html
│   ├── assets/
│   │   ├── css/styles.css
│   │   ├── js/main.js
│   │   ├── images/tim-gibson-headshot.webp
│   │   └── documents/tim-gibson-resume.pdf
│   ├── CNAME
│   ├── robots.txt
│   ├── sitemap.xml
│   └── 404.html
├── development/
├── docs/
├── .github/workflows/deploy-pages.yml
├── .gitignore
└── README.md
```

The `development/` directory will be reserved for local drafts or experiments and will not be published. The production site itself will not require Node.js, a package manager, Jekyll, or a compilation step.

## Deployment and Domain

A GitHub Actions workflow will upload `production/` as the GitHub Pages artifact and deploy it from the `main` branch. The workflow will use GitHub's built-in repository token, so a deploy key is not required.

Deployment will follow this sequence:

1. Publish and verify `https://the-ad-guy.github.io`.
2. Add `theadguy.org` in the repository's Pages settings.
3. Configure the domain's DNS records.
4. Wait for GitHub's domain and certificate checks.
5. Enable HTTPS enforcement.

The production artifact will include a `CNAME` file containing `theadguy.org`.

## Content Sources

- Tim's latest resume document and approved resume language
- The supplied headshot at `images/full headshot.jpg`
- Public project repositories and Chrome Web Store listing
- Previously supplied quantified performance results

No private client names, proprietary source code, or confidential performance data will be exposed.

## Search, Sharing, and Accessibility

Each page will have a unique title and description, canonical metadata, Open Graph metadata, and meaningful heading structure. The site will include a sitemap and robots file. The headshot will have descriptive alternative text, decorative elements will remain hidden from assistive technology, and text contrast will meet WCAG AA targets.

No analytics or advertising trackers will be installed in the first version. This keeps the initial site private by design and avoids adding consent requirements before Tim chooses a measurement platform.

## Validation

Before deployment, the site will be checked for:

- Valid internal links and public project links
- Correct navigation state on all three pages
- Responsive layout at common phone, tablet, and desktop widths
- Keyboard navigation and visible focus treatment
- Missing assets and console errors
- Accurate resume and project copy
- Successful GitHub Pages deployment from `production/`
- Working PDF download

## Out of Scope for Version One

- Blog or content-management system
- Contact form or server-side processing
- User accounts, databases, or external APIs
- Tracking scripts or cookie consent interface
- Complex animation or custom illustration
- Separate public staging environment

