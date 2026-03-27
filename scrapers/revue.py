"""
Test scraper for Revue calendar page.
Parses embedded event JSON from /calendar/ and writes the same item shape the project expects.
"""

from urllib.request import Request, urlopen
from urllib.parse import urljoin
from datetime import datetime
from .base import BaseScraper

import sys
import os
import re
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import THEATERS

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
CAL_URL = 'https://revuecinema.ca/calendar/'


class RevueCalendarScraper(BaseScraper):
    MIN_EXPECTED_FILMS = 20

    def __init__(self):
        config = THEATERS['revue']
        super().__init__('revue_calendar_test', config['name'], CAL_URL)

    def fetch_html(self):
        req = Request(self.url, headers={'User-Agent': UA})
        with urlopen(req, timeout=30) as r:
            return r.read().decode('utf-8', errors='ignore')

    def scrape(self):
        print(f"📄 Fetching calendar page source: {self.url}")
        html = self.fetch_html()
        print(f"✅ Calendar page source fetched ({len(html)} bytes)")

        # The page contains repeated event objects like:
        # {"title":"...","start":"2026-04-09 21:30:00","url":"https://..."}
        pattern = re.compile(r'\{"title":"(.*?)","start":"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})","url":"(https://revuecinema\.ca/films/.*?)"\}')
        matches = pattern.findall(html)
        print(f"🎬 [{self.theater_name}] Found {len(matches)} raw calendar event objects")

        seen = set()
        for raw_title, raw_start, raw_url in matches:
            title = bytes(raw_title, 'utf-8').decode('unicode_escape')
            link = bytes(raw_url, 'utf-8').decode('unicode_escape')
            start = datetime.strptime(raw_start, '%Y-%m-%d %H:%M:%S')
            showtime = start.strftime('%a %b %d, %I:%M %p').replace(' 0', ' ')
            key = (title, showtime, link)
            if key in seen:
                continue
            seen.add(key)
            self.add_film(title, showtime, urljoin(self.url, link))

        print(f"🎬 [{self.theater_name}] Final parsed films: {len(self.films)}")
        if len(self.films) < self.MIN_EXPECTED_FILMS:
            raise RuntimeError(f"Calendar-page parse produced suspiciously low film count ({len(self.films)} < {self.MIN_EXPECTED_FILMS})")
        return self.films


if __name__ == '__main__':
    scraper = RevueCalendarScraper()
    films = scraper.run()
    print(f"\n🎬 Total films scraped: {len(films)}")
