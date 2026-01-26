"""
Revue Cinema scraper - handles "Load More" pagination.
"""

from selenium.webdriver.common.by import By
from .base import BaseScraper

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import THEATERS


class RevueScraper(BaseScraper):
    """Scraper for Revue Cinema (revuecinema.ca)"""
    
    def __init__(self):
        config = THEATERS["revue"]
        super().__init__("revue", config["name"], config["url"])
        
    def scrape(self):
        # Click "Load More" until all films are loaded
        self.click_load_more("//a[text()='Load More']")
        
        # Parse film blocks
        film_blocks = self.driver.find_elements(By.CLASS_NAME, "brxe-sdlpwn")
        print(f"🎬 [{self.theater_name}] Found {len(film_blocks)} total films")
        
        for block in film_blocks:
            # Get title and link
            try:
                title_tag = block.find_element(By.TAG_NAME, "h5").find_element(By.TAG_NAME, "a")
                title = title_tag.text.strip()
                link = title_tag.get_attribute("href")
            except Exception:
                title, link = "Untitled", None
                
            # Get showtime
            try:
                showtime_tag = block.find_element(By.CLASS_NAME, "brxe-ndxpjc")
                showtime = showtime_tag.text.strip()
            except Exception:
                showtime = "No time listed"
                
            if title and showtime and showtime != "No time listed":
                self.add_film(title, showtime, link)
                
        return self.films


if __name__ == "__main__":
    scraper = RevueScraper()
    films = scraper.run()
    print(f"\n🎬 Total films scraped: {len(films)}")
