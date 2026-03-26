"""
Revue Cinema scraper.

2026-03-26 rewrite:
- Parse the richer server-rendered HTML directly with a realistic browser user-agent.
- Avoid brittle Selenium/Bricks load-more interactions for cron reliability.
- Use the repeated `.brxe-sdlpwn` card markup found in the raw page source.
"""

from urllib.request import Request, urlopen
from urllib.parse import urljoin
from html import unescape
from .base import BaseScraper

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import THEATERS


UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'


class RevueScraper(BaseScraper):
    """Scraper for Revue Cinema (revuecinema.ca) using direct HTML parsing."""

    MIN_EXPECTED_FILMS = 20

    def __init__(self):
        config = THEATERS['revue']
        super().__init__('revue', config['name'], config['url'])

    def fetch_html(self):
        req = Request(self.url, headers={'User-Agent': UA})
        with urlopen(req, timeout=30) as r:
            return r.read().decode('utf-8', errors='ignore')

    def scrape(self):
        print(f"📄 Fetching page source: {self.url}")
        html = self.fetch_html()
        print(f"✅ Page source fetched ({len(html)} bytes)")

        pattern = re.compile(
            r'<div class="brxe-sdlpwn brxe-div(?: bricks-lazy-hidden)?">\s*'
            r'<h5 class="brxe-xqcpwc brxe-heading"><a href="([^"]+)">(.*?)</a></h5>\s*'
            r'<div class="brxe-eizvou brxe-div(?: bricks-lazy-hidden)?">\s*'
            r'<div class="brxe-ndxpjc brxe-text-basic">(.*?)</div>',
            re.S,
        )
        matches = pattern.findall(html)
        print(f"🎬 [{self.theater_name}] Found {len(matches)} raw film cards in HTML source")

        seen = set()
        for href, raw_title, raw_showtime in matches:
            title = ' '.join(unescape(re.sub(r'<[^>]+>', ' ', raw_title)).split())
            showtime = ' '.join(unescape(re.sub(r'<[^>]+>', ' ', raw_showtime)).split())
            link = urljoin(self.url, unescape(href.strip()))
            if not title or not showtime:
                continue
            key = (title, showtime, link)
            if key in seen:
                continue
            seen.add(key)
            self.add_film(title, showtime, link)

        print(f"🎬 [{self.theater_name}] Final parsed films: {len(self.films)}")

        if len(self.films) < self.MIN_EXPECTED_FILMS:
            raise RuntimeError(
                f"Direct HTML parse for Revue produced suspiciously low film count ({len(self.films)} < {self.MIN_EXPECTED_FILMS})"
            )

        return self.films


if __name__ == '__main__':
    scraper = RevueScraper()
    films = scraper.run()
    print(f"\n🎬 Total films scraped: {len(films)}")
    if len(films) < scraper.MIN_EXPECTED_FILMS:
        sys.exit(1)
