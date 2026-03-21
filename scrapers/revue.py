"""
Revue Cinema scraper - handles "Load More" pagination.
"""

from selenium.webdriver.common.by import By
from .base import BaseScraper

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import THEATERS


class RevueScraper(BaseScraper):
    """Scraper for Revue Cinema (revuecinema.ca)"""

    MIN_EXPECTED_FILMS = 80
    
    def __init__(self):
        config = THEATERS["revue"]
        super().__init__("revue", config["name"], config["url"])
        
    def scrape(self):
        # Give the page extra time to settle/render before pagination.
        time.sleep(4)

        initial_title = self.driver.title
        initial_blocks = self.driver.find_elements(By.CLASS_NAME, "brxe-sdlpwn")
        load_more_links = self.driver.find_elements(By.XPATH, "//a[text()='Load More']")
        challenge_markers = {
            "loading-verifying": len(self.driver.find_elements(By.CLASS_NAME, "loading-verifying")),
            "lds-ring": len(self.driver.find_elements(By.CLASS_NAME, "lds-ring")),
            "cf-challenge-running": len(self.driver.find_elements(By.CLASS_NAME, "cf-challenge-running")),
        }
        print(f"ℹ️ [{self.theater_name}] Initial title: {initial_title}")
        print(f"ℹ️ [{self.theater_name}] Initial blocks: {len(initial_blocks)} | Load More links: {len(load_more_links)} | Challenge markers: {challenge_markers}")

        # Some bad runs appear to be partial/lazy/challenge states; a refresh can help.
        if len(initial_blocks) < 20:
            print(f"⚠️ [{self.theater_name}] Very low initial block count ({len(initial_blocks)}); waiting and refreshing once")
            time.sleep(4)
            self.driver.refresh()
            time.sleep(6)
            refreshed_title = self.driver.title
            refreshed_blocks = self.driver.find_elements(By.CLASS_NAME, "brxe-sdlpwn")
            refreshed_load_more = self.driver.find_elements(By.XPATH, "//a[text()='Load More']")
            refreshed_markers = {
                "loading-verifying": len(self.driver.find_elements(By.CLASS_NAME, "loading-verifying")),
                "lds-ring": len(self.driver.find_elements(By.CLASS_NAME, "lds-ring")),
                "cf-challenge-running": len(self.driver.find_elements(By.CLASS_NAME, "cf-challenge-running")),
            }
            print(f"ℹ️ [{self.theater_name}] After refresh title: {refreshed_title}")
            print(f"ℹ️ [{self.theater_name}] After refresh blocks: {len(refreshed_blocks)} | Load More links: {len(refreshed_load_more)} | Challenge markers: {refreshed_markers}")

        # Click "Load More" until all films are loaded
        self.click_load_more("//a[text()='Load More']", max_clicks=12, wait_s=1.8)
        
        # Parse film blocks
        film_blocks = self.driver.find_elements(By.CLASS_NAME, "brxe-sdlpwn")
        print(f"🎬 [{self.theater_name}] Found {len(film_blocks)} total films")

        if len(film_blocks) < self.MIN_EXPECTED_FILMS:
            final_title = self.driver.title
            final_load_more = self.driver.find_elements(By.XPATH, "//a[text()='Load More']")
            final_markers = {
                "loading-verifying": len(self.driver.find_elements(By.CLASS_NAME, "loading-verifying")),
                "lds-ring": len(self.driver.find_elements(By.CLASS_NAME, "lds-ring")),
                "cf-challenge-running": len(self.driver.find_elements(By.CLASS_NAME, "cf-challenge-running")),
            }
            raise RuntimeError(
                f"Suspiciously low Revue film count ({len(film_blocks)} < {self.MIN_EXPECTED_FILMS}); title={final_title!r}; load_more_links={len(final_load_more)}; challenge_markers={final_markers}; likely anti-bot/challenge/intermittent site issue"
            )
        
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
    if len(films) < scraper.MIN_EXPECTED_FILMS:
        sys.exit(1)
