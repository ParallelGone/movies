"""
Fox Theatre scraper - handles infinite scroll page.
"""

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
        
    def scrape(self):
        # Scroll to load all showtimes (infinite scroll)
        self.scroll_to_load_all("span[data-date]")
        
        # Parse the loaded content
        seen = set()
        blocks = self.driver.find_elements(By.CSS_SELECTOR, "div[data-element_type='container']")
        print(f"🔍 [{self.theater_name}] Checking {len(blocks)} containers")
        
        for block in blocks:
            # Get title
            title = safe_find_text(block, "h4.elementor-heading-title")
            if not title:
                continue
                
            # Get link
            link = safe_find_attr(block, "a[href*='/movies/']", "href")
            if not link:
                link = self.url
                
            # Get all showtimes for this film
            time_elements = block.find_elements(By.CSS_SELECTOR, "span[data-date]")
            
            for t in time_elements:
                raw_time = t.text.strip()
                raw_date = t.get_attribute("data-date")
                
                if not raw_time or not raw_date:
                    continue
                    
                # Validate time format
                if ":" not in raw_time or not ("am" in raw_time.lower() or "pm" in raw_time.lower()):
                    continue
                    
                # Format the showtime
                try:
                    dt = datetime.strptime(raw_date, "%Y-%m-%d")
                    formatted_date = dt.strftime("%A, %B %d").replace(" 0", " ")
                except ValueError:
                    formatted_date = raw_date
                    
                showtime = f"{formatted_date}, {raw_time}"
                
                # Deduplicate
                key = (title, showtime)
                if key not in seen:
                    seen.add(key)
                    self.add_film(title, showtime, link)
                    
        return self.films


if __name__ == "__main__":
    scraper = FoxScraper()
    films = scraper.run()
    print(f"\n🎬 Total films scraped: {len(films)}")
