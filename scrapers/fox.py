"""
Fox Theatre scraper - handles infinite scroll page.
"""

from collections import Counter, defaultdict
from datetime import datetime
from selenium.webdriver.common.by import By
from .base import BaseScraper, safe_find_text, safe_find_attr

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import THEATERS


class FoxScraper(BaseScraper):
    """Scraper for Fox Theatre (foxtheatre.ca)"""
    
    def __init__(self):
        config = THEATERS["fox"]
        super().__init__("fox", config["name"], config["url"])

    def _movie_links(self):
        """Collect unique movie detail links from the now-showing page."""
        links = {}
        blocks = self.driver.find_elements(By.CSS_SELECTOR, "div[data-element_type='container']")
        print(f"🔍 [{self.theater_name}] Checking {len(blocks)} containers")
        for block in blocks:
            title = safe_find_text(block, "h4.elementor-heading-title")
            link = safe_find_attr(block, "a[href*='/movies/']", "href")
            if not title or not link:
                continue
            links[link] = title.strip()
        print(f"🎬 [{self.theater_name}] Found {len(links)} unique movie pages")
        return links

    def _scrape_movie_page(self, title, link):
        films = []
        if not self.load_page(link):
            return films

        items = self.driver.find_elements(By.CSS_SELECTOR, ".showtimes-lists .item")
        seen = set()
        for item in items:
            raw_date = safe_find_text(item, "span.date")
            raw_time = safe_find_text(item, "span.time")
            ticket_link = safe_find_attr(item, "a[href*='ticketsearchcriteria.aspx']", "href") or link

            if not raw_date or not raw_time:
                continue
            if ":" not in raw_time or not ("am" in raw_time.lower() or "pm" in raw_time.lower()):
                continue

            showtime = f"{raw_date.strip()}, {raw_time.strip()}"
            key = (title, showtime)
            if key in seen:
                continue
            seen.add(key)
            films.append({
                "title": title,
                "showtime": showtime,
                "link": ticket_link,
                "source": self.theater_name,
            })
        return films

    def scrape(self):
        # Scroll listing page just enough to load movie cards, then use movie pages as source of truth.
        self.scroll_to_load_all("a[href*='/movies/']")
        movie_links = self._movie_links()

        all_films = []
        for idx, (link, title) in enumerate(movie_links.items(), start=1):
            print(f"🔎 [{self.theater_name}] ({idx}/{len(movie_links)}) {title}")
            all_films.extend(self._scrape_movie_page(title, link))

        counts = Counter(x["title"] for x in all_films)
        for title, count in counts.most_common(10):
            if count > 20:
                print(f"⚠️  [{self.theater_name}] High showtime count after movie-page scrape: {title} -> {count}")

        return all_films


if __name__ == "__main__":
    scraper = FoxScraper()
    films = scraper.run()
    print(f"\n🎬 Total films scraped: {len(films)}")
