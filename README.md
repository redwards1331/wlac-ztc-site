WLAC ZTC Course Finder - GitHub Pages + Auto-update

Contents:
- index.html, styles.css, scripts.js: static site (loads ztc_live.csv)
- fetch_ztc.py: Selenium-based scraper to extract ZTC course listings from WLAC/LACCD site
- requirements.txt: Python deps
- .github/workflows/update-ztc.yml: scheduled GitHub Action to run scraper and commit ztc_live.csv

How to use:
1. Create a new GitHub repo (public).
2. Upload all files from this repo into the repository root.
3. In Actions, enable workflows. GitHub will run the provided workflow on schedule.
4. Enable GitHub Pages in Settings -> Pages -> Branch main, folder root.
5. Visit https://<yourusername>.github.io/<repo>/ to see the site.

Notes & troubleshooting:
- The scraper uses Selenium + Chromium. GitHub Actions installs chromium & chromedriver via apt-get.
- Web page layouts change. If scraping fails, inspect page structure and update selectors in fetch_ztc.py.
- If the WLAC site blocks automated access, consider switching to a Google Sheet as the source and updating that sheet during maintenence.

Security:
- Keep the repo public if you want Pages to be public. If private, Pages from private repos require a GitHub Pro/Org account.

