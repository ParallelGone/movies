"""
Paradise Theatre scraper - simple page load with showtime blocks.
"""

from selenium.webdriver.common.by import By
from .base import BaseScraper

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import THEATERS


class ParadiseScraper(BaseScraper):
    """Scraper for Paradise Theatre (paradiseonbloor.com)"""
    
    def __init__(self):
        config = THEATERS["paradise"]
        super().__init__("paradise", config["name"], config["url"])
        
    def scrape(self):
        film_blocks = self.driver.find_elements(By.CLASS_NAME, "showtimes-description")
        print(f"✅ [{self.theater_name}] Found {len(film_blocks)} film blocks")
        
        for block in film_blocks:
            # Get title and link
            try:
                title_tag = block.find_element(By.CLASS_NAME, "show-title").find_element(By.TAG_NAME, "a")
                title = title_tag.text.strip()
                link = title_tag.get_attribute("href")
            except Exception:
                title, link = "Untitled", None
                
            # Get date
            try:
                date_tag = block.find_element(By.CLASS_NAME, "selected-date")
                date = date_tag.text.strip().replace("\n", " ")
            except Exception:
                date = "Unknown"
                
            # Get showtimes
            try:
                time_tags = block.find_elements(By.CLASS_NAME, "showtime")
                times = [t.text.strip() for t in time_tags if t.text.strip()]
            except Exception:
                times = []
                
            # Add each showtime as a separate entry
            for time_str in times:
                showtime = f"{date}, {time_str}"
                self.add_film(title, showtime, link)
                
        return self.films


if __name__ == "__main__":
    scraper = ParadiseScraper()
    films = scraper.run()
    print(f"\n🎬 Total films scraped: {len(films)}")
