# Tim Gibson Portfolio

Static professional portfolio for [theadguy.org](https://theadguy.org), hosted with GitHub Pages.

## Structure

```text
production/                 Deployable website only
  index.html                Home page
  projects/index.html       Projects page
  resume/index.html         Web resume
  assets/                   Shared CSS, JavaScript, image, and PDF
development/                Local utilities, tests, and source assets
docs/                       Design and implementation documentation
.github/workflows/          GitHub Pages deployment
```

GitHub Actions publishes only the contents of `production/`.

## Preview locally

From the repository root:

```powershell
python -m http.server 8000 --directory production
```

Then open `http://localhost:8000`.

## Validate

```powershell
python -m unittest development.tests.test_site -v
```

## Publish

Push to `main`. The `Deploy to GitHub Pages` workflow uploads `production/` and publishes it through the `github-pages` environment.

For the initial launch, select **GitHub Actions** under **Settings > Pages > Build and deployment > Source**. Verify the default GitHub Pages address before connecting the custom domain and enabling HTTPS.
