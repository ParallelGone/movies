"""
Base scraper class with common functionality for all theater scrapers.
Eliminates code duplication across individual scrapers.
"""

import json
import time
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BROWSER_OPTIONS, SCRAPE_SETTINGS, OUTPUT_DIR


class BaseScraper(ABC):
    """
    Abstract base class for all theater scrapers.
    Handles driver setup, common operations, and JSON export.
    """
    
    def __init__(self, theater_id: str, theater_name: str, url: str):
        self.theater_id = theater_id
        self.theater_name = theater_name
        self.url = url
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.films: List[Dict] = []
        
    def setup_driver(self) -> None:
        """Initialize Chrome WebDriver with configured options."""
        options = Options()
        
        if BROWSER_OPTIONS.get("headless"):
            options.add_argument("--headless")
        if BROWSER_OPTIONS.get("no_sandbox"):
            options.add_argument("--no-sandbox")
        if BROWSER_OPTIONS.get("disable_dev_shm"):
            options.add_argument("--disable-dev-shm-usage")
        if BROWSER_OPTIONS.get("start_maximized"):
            options.add_argument("--start-maximized")
            
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def load_page(self, wait_time: Optional[int] = None) -> None:
        """Navigate to URL and wait for content to load."""
        if wait_time is None:
            wait_time = SCRAPE_SETTINGS["page_load_wait"]
            
        self.driver.get(self.url)
        print(f"📄 [{self.theater_name}] Page loaded: {self.driver.title}")
        time.sleep(wait_time)
        
    def scroll_to_load_all(self, check_selector: str, max_attempts: Optional[int] = None) -> int:
        """
        Scroll page to trigger infinite scroll loading.
        Returns the count of elements found.
        """
        if max_attempts is None:
            max_attempts = SCRAPE_SETTINGS["max_scroll_attempts"]
            
        actions = ActionChains(self.driver)
        body = self.driver.find_element(By.TAG_NAME, "body")
        
        last_count = 0
        stagnant_rounds = 0
        
        while stagnant_rounds < max_attempts:
            elements = self.driver.find_elements(By.CSS_SELECTOR, check_selector)
            current_count = len(elements)
            
            print(f"🔄 [{self.theater_name}] {current_count} items loaded...")
            
            if current_count == last_count:
                stagnant_rounds += 1
            else:
                stagnant_rounds = 0
                last_count = current_count
                
            self.driver.execute_script("window.scrollBy(0, 1000);")
            try:
                actions.move_to_element_with_offset(body, 10, 10).perform()
            except Exception:
                pass
            time.sleep(SCRAPE_SETTINGS["scroll_wait"])
            
        print(f"✅ [{self.theater_name}] Finished scrolling, {last_count} items found.")
        return last_count
        
    def click_load_more(self, button_xpath: str, max_clicks: Optional[int] = None) -> int:
        """
        Click "Load More" button repeatedly until exhausted.
        Returns the number of successful clicks.
        """
        if max_clicks is None:
            max_clicks = SCRAPE_SETTINGS["max_load_more_clicks"]
            
        clicks = 0
        
        while clicks < max_clicks:
            try:
                load_more = self.driver.find_element(By.XPATH, button_xpath)
                ActionChains(self.driver).move_to_element(load_more).perform()
                time.sleep(1)
                load_more.click()
                print(f"🔄 [{self.theater_name}] Clicked 'Load More' ({clicks + 1})")
                time.sleep(SCRAPE_SETTINGS["scroll_wait"])
                clicks += 1
            except Exception:
                print(f"✅ [{self.theater_name}] No more 'Load More' button found.")
                break
                
        return clicks
        
    def add_film(self, title: str, showtime: str, link: Optional[str] = None) -> None:
        """Add a film entry to the results list."""
        if not title or not showtime:
            return
            
        self.films.append({
            "title": title.strip(),
            "showtime": showtime.strip(),
            "link": link or self.url,
            "source": self.theater_name
        })
        
    def save_json(self) -> str:
        """Save scraped films to JSON file. Returns filepath."""
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filepath = os.path.join(OUTPUT_DIR, f"{self.theater_id}_films.json")
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.films, f, indent=2, ensure_ascii=False)
            
        print(f"💾 [{self.theater_name}] Saved {len(self.films)} films to {filepath}")
        return filepath
        
    def cleanup(self) -> None:
        """Close the browser and clean up resources."""
        if self.driver:
            self.driver.quit()
            print(f"👋 [{self.theater_name}] Browser closed.")
            
    @abstractmethod
    def scrape(self) -> List[Dict]:
        """
        Main scraping logic - must be implemented by each theater scraper.
        Returns list of film dictionaries.
        """
        pass
        
    def run(self) -> List[Dict]:
        """
        Execute the full scraping workflow with error handling.
        """
        try:
            self.setup_driver()
            self.load_page()
            self.scrape()
            self.save_json()
            return self.films
        except Exception as e:
            print(f"❌ [{self.theater_name}] Error: {e}")
            return []
        finally:
            self.cleanup()


def safe_find_text(element, selector: str, by: str = By.CSS_SELECTOR) -> str:
    """Safely extract text from an element, returning empty string on failure."""
    try:
        return element.find_element(by, selector).text.strip()
    except Exception:
        return ""


def safe_find_attr(element, selector: str, attr: str, by: str = By.CSS_SELECTOR) -> str:
    """Safely extract an attribute from an element."""
    try:
        return element.find_element(by, selector).get_attribute(attr) or ""
    except Exception:
        return ""
