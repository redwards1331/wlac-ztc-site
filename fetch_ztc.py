#!/usr/bin/env python3
"""fetch_ztc.py
Scrapes WLAC / LACCD class search for Zero Textbook Cost (ZTC) courses and writes ztc_live.csv.

Notes:
- This script uses Selenium + Chromium. In GitHub Actions we install chromium & chromedriver.
- The site structure can change; selectors are conservative and include fallbacks.
"""

import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from bs4 import BeautifulSoup

# URL to the WLAC class search (may redirect to LACCD search)
START_URL = 'https://www.laccd.edu/students/class-search'  # adjust if needed

def start_driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # On GitHub Actions, chromium binary should be available at /usr/bin/chromium-browser or /usr/bin/chromium
    # Selenium will auto-find chromedriver if installed.
    return webdriver.Chrome(options=options)

def try_click_ztc_filter(driver):
    # Attempt to find elements containing "Zero Textbook" or "ZTC" and click them.
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    candidates = []
    for txt in ['Zero Textbook', 'Zero-Textbook', 'Zero Textbook Cost', 'ZTC', 'Zero Cost Textbooks']:
        for el in soup.find_all(string=lambda s: s and txt.lower() in s.lower()):
            candidates.append(el)
    # Try to click corresponding elements by locating a parent with clickable attributes
    for el in candidates:
        try:
            # find element by xpath using text
            xpath = f"//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{el.strip().lower()}')]"
            elements = driver.find_elements('xpath', xpath)
            for e in elements:
                try:
                    e.click()
                    return True
                except Exception:
                    pass
        except Exception:
            pass
    return False

def extract_courses_from_soup(soup):
    results = []
    # Look for common patterns: table rows, course cards, list items
    # Try table rows first
    table_rows = soup.select('tr')
    if table_rows and len(table_rows) > 5:
        for tr in table_rows:
            text = ' '.join(tr.stripped_strings)
            if not text:
                continue
            # crude parse: split by multiple spaces to find course code-like tokens
            parts = text.split()
            # heuristic: if contains a department/course token like 'ENGLISH' or 'MATH' followed by a number
            results.append({'raw': text})
    # fallback: look for divs with class containing 'course' or 'result'
    if not results:
        cards = soup.select('div[class*="course"], div[class*="result"], li[class*="course"], li[class*="result"]')
        for c in cards:
            text = ' '.join(c.stripped_strings)
            if text:
                results.append({'raw': text})
    # Return results as list of dicts (best-effort)
    out = []
    for r in results:
        raw = r.get('raw','')
        # simple CSV fields: Course, Description, Department, Term, Instructor, Link
        out.append({
            'Course': raw.split(' - ')[0][:80],
            'Description': raw[:250],
            'Department': '',
            'Term': '',
            'Instructor': '',
            'Link': ''
        })
    return out

def main():
    print('Starting browser...')
    driver = start_driver()
    driver.get(START_URL)
    time.sleep(3)
    # Try to click ZTC filter if available
    try:
        clicked = try_click_ztc_filter(driver)
    except Exception:
        clicked = False
    # Attempt to click search buttons if any
    try:
        # common search button candidates
        for sel in ['button[type=submit]', 'button.search', 'input[type=submit]']:
            try:
                el = driver.find_element('css selector', sel)
                el.click()
                time.sleep(2)
            except Exception:
                pass
    except Exception:
        pass
    # Give page time to render results
    time.sleep(4)
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    courses = extract_courses_from_soup(soup)
    # Write CSV
    out_file = 'ztc_live.csv'
    with open(out_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Course','Description','Department','Term','Instructor','Link'])
        writer.writeheader()
        for row in courses:
            writer.writerow(row)
    print(f'Wrote {len(courses)} rows to {out_file}')
    driver.quit()

if __name__ == '__main__':
    main()
