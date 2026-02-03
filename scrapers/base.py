"""
Base Scraper Class for Toronto Rep Cinema Calendar

Provides common functionality for all theater scrapers including:
- Chrome WebDriver setup with Windows compatibility
- Page loading and waiting
- JSON file saving
- Error handling

Updated with:
- Unicode/emoji encoding fixes for Windows
- ChromeDriver warning suppression
- Clean console output
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import time
from pathlib import Path
from typing import List, Dict
import sys
import io
import os

# ============================================================
# Windows Unicode/Emoji Fix
# Prevents UnicodeEncodeError when printing emoji on Windows
# ============================================================
if sys.platform == 'win32':
    # For Python 3.7+
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass
    else:
        # For older Python versions
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer,
                encoding='utf-8',
                errors='replace',
                line_buffering=True
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer,
                encoding='utf-8',
                errors='replace',
                line_buffering=True
            )
        except Exception:
            pass


class BaseScraper:
    """Base class for all theater scrapers."""
    
    def __init__(self, theater_id: str, theater_name: str, theater_url: str):
        """
        Initialize base scraper.
        
        Args:
            theater_id: Short ID for the theater (e.g., "fox", "paradise", "tiff")
            theater_name: Full name of the theater (e.g., "Fox Theatre")
            theater_url: URL of the theater's schedule page
        """
        self.theater_id = theater_id
        self.theater_name = theater_name
        self.theater_url = theater_url
        self.url = theater_url  # backward-compat alias used by older scrapers
        self.driver = None
        self.films = []
        
        # Set output file path: data/{theater_id}_films.json
        self.output_file = Path('data') / f'{theater_id}_films.json'
        
        # Ensure data directory exists
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
    
    def setup_driver(self):
        """
        Set up Chrome WebDriver with complete output suppression for Windows.
        
        This configuration:
        - Runs Chrome in headless mode (no visible browser)
        - Completely suppresses all ChromeDriver console output
        - Prevents Unicode decode errors on Windows
        - Works with Python 3.13+
        
        Returns:
            WebDriver: Configured Chrome WebDriver instance
        """
        import subprocess
        
        options = webdriver.ChromeOptions()
        
        # Headless mode configuration
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # Aggressive output suppression
        options.add_argument('--log-level=3')
        options.add_argument('--silent')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # Disable features that generate output
        options.add_argument('--disable-usb-keyboard-detect')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-sync')
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Set user agent
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # Windows-specific encoding
        if sys.platform == 'win32':
            os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        try:
            # Create service with output redirection
            service = webdriver.ChromeService(log_path=os.devnull)
            
            # Windows-specific: Suppress subprocess window
            if sys.platform == 'win32':
                # Hide the ChromeDriver console window
                CREATE_NO_WINDOW = 0x08000000
                service.creation_flags = CREATE_NO_WINDOW
            
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(30)
            return driver
            
        except Exception as e:
            print(f"❌ Error setting up Chrome driver: {e}")
            raise
    
    def load_page(self, url: str = None) -> bool:
        """
        Load a page and wait for it to be ready.
        
        Args:
            url: URL to load (default: self.theater_url)
            
        Returns:
            bool: True if page loaded successfully, False otherwise
        """
        if url is None:
            url = self.theater_url
        
        try:
            print(f"📄 Loading page: {url}")
            self.driver.get(url)
            
            # Wait for body element to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Small delay to let JavaScript render
            time.sleep(2)
            
            print(f"✅ Page loaded successfully")
            return True
            
        except TimeoutException:
            print(f"❌ Timeout loading page: {url}")
            return False
        except Exception as e:
            print(f"❌ Error loading page: {e}")
            return False
    
    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """
        Wait for an element to be present on the page.
        
        Args:
            by: Selenium By locator type (e.g., By.CSS_SELECTOR)
            value: Locator value (e.g., ".movie-card")
            timeout: Maximum seconds to wait
            
        Returns:
            WebElement if found, None if timeout
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            print(f"⚠️  Element not found: {value}")
            return None
    
    def save_to_json(self, data: List[Dict] = None) -> bool:
        """
        Save films data to JSON file.
        
        Args:
            data: List of film dictionaries to save (default: self.films)
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        if data is None:
            data = self.films
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved {len(data)} films to {self.output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving to JSON: {e}")
            return False
    
    def cleanup(self):
        """Close the browser and clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                print(f"🌐 Browser closed")
            except Exception as e:
                print(f"⚠️  Error closing browser: {e}")
    
    def scrape(self) -> List[Dict]:
        """
        Main scraping method - to be implemented by subclasses.
        
        Returns:
            List[Dict]: List of film dictionaries with keys:
                - title: Film title
                - showtime: Full showtime string (e.g., "Monday, January 26, 7:00 PM")
                - link: URL to film page or tickets
                - source: Theater name
        """
        raise NotImplementedError("Subclasses must implement scrape() method")
    
    def scroll_to_load_all(self, item_selector: str, max_attempts: int = 25, wait_s: float = 1.5) -> None:
        """Scroll down until the number of elements matching item_selector stops increasing."""
        import time
        last_count = -1
        stable = 0
        for _ in range(max_attempts):
            try:
                items = self.driver.find_elements(By.CSS_SELECTOR, item_selector)
                count = len(items)
                print(f"🔄 [{self.theater_name}] {count} items loaded...")
                if count == last_count:
                    stable += 1
                else:
                    stable = 0
                    last_count = count

                if stable >= 3:
                    break

                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(wait_s)
            except Exception:
                time.sleep(wait_s)
        print(f"✅ [{self.theater_name}] Finished scrolling, {max(last_count,0)} items found.")

    def click_load_more(self, load_more_xpath: str, max_clicks: int = 10, wait_s: float = 1.2) -> None:
        """Click a 'Load More' element repeatedly until it disappears."""
        import time
        for i in range(max_clicks):
            try:
                btn = self.driver.find_element(By.XPATH, load_more_xpath)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(0.3)
                btn.click()
                print(f"🔄 [{self.theater_name}] Clicked 'Load More' ({i+1})")
                time.sleep(wait_s)
            except Exception:
                break

    def run(self) -> List[Dict]:
        """
        Complete scraping workflow: setup → scrape → save → cleanup.
        
        Returns:
            List[Dict]: List of scraped films
        """
        print("\n" + "="*60)
        print(f"📋 Scraping {self.theater_name.upper()}")
        print("="*60)
        
        try:
            # Setup
            self.driver = self.setup_driver()
            
            # Load page
            if not self.load_page():
                print(f"❌ Failed to load page")
                return []
            
            # Scrape (implemented by subclass)
            self.films = self.scrape()
            
            # Save results
            if self.films:
                self.save_to_json()
                print(f"✅ Successfully scraped {len(self.films)} films")
            else:
                print(f"⚠️  No films found")
            
            return self.films
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            import traceback
            traceback.print_exc()
            return []
            
        finally:
            # Always cleanup
            self.cleanup()
    
    def add_film(self, title: str, showtime: str, link: str = "") -> None:
        """Back-compat helper used by existing scrapers.

        Appends a film/screening dict to self.films.
        """
        if not title:
            return
        self.films.append({
            "title": title.strip(),
            "showtime": showtime.strip() if showtime else "",
            "link": link.strip() if link else self.url,
            "source": self.theater_name,
        })

    def format_showtime(self, date: str, time: str) -> str:
        """
        Format a showtime string in the standard format.
        
        Args:
            date: Date string (e.g., "Monday, January 26")
            time: Time string (e.g., "7:00 PM")
            
        Returns:
            str: Formatted showtime (e.g., "Monday, January 26, 7:00 PM")
        """
        # Clean up date and time
        date = date.strip()
        time = time.strip()
        
        # Combine
        if time:
            return f"{date}, {time}"
        else:
            return date
    
    def safe_get_text(self, element, default: str = "") -> str:
        """
        Safely get text from an element.
        
        Args:
            element: Selenium WebElement
            default: Default value if element is None or has no text
            
        Returns:
            str: Element text or default value
        """
        try:
            if element is None:
                return default
            text = element.text.strip()
            return text if text else default
        except Exception:
            return default
    
    def safe_get_attribute(self, element, attribute: str, default: str = "") -> str:
        """
        Safely get an attribute from an element.
        
        Args:
            element: Selenium WebElement
            attribute: Attribute name (e.g., "href")
            default: Default value if element is None or attribute missing
            
        Returns:
            str: Attribute value or default value
        """
        try:
            if element is None:
                return default
            value = element.get_attribute(attribute)
            return value if value else default
        except Exception:
            return default


# ============================================================
# Standalone Helper Functions
# (For backward compatibility with existing scrapers)
# ============================================================

def safe_find_text(element, selector: str, default: str = "") -> str:
    """
    Safely find and extract text from a child element.
    
    Args:
        element: Parent element to search within
        selector: CSS selector for child element
        default: Default value if element not found
        
    Returns:
        str: Element text or default value
    """
    try:
        if element is None:
            return default
        child = element.find_element(By.CSS_SELECTOR, selector)
        text = child.text.strip()
        return text if text else default
    except NoSuchElementException:
        return default
    except Exception:
        return default


def safe_find_attr(element, selector: str, attribute: str, default: str = "") -> str:
    """
    Safely find a child element and get its attribute.
    
    Args:
        element: Parent element to search within
        selector: CSS selector for child element
        attribute: Attribute name to get (e.g., "href")
        default: Default value if element not found
        
    Returns:
        str: Attribute value or default value
    """
    try:
        if element is None:
            return default
        child = element.find_element(By.CSS_SELECTOR, selector)
        value = child.get_attribute(attribute)
        return value if value else default
    except NoSuchElementException:
        return default
    except Exception:
        return default


# ============================================================
# Example usage / testing
# ============================================================
if __name__ == "__main__":
    print("BaseScraper class - Base functionality for all theater scrapers")
    print("\nThis is a base class and should not be run directly.")
    print("Use specific scraper classes (fox.py, paradise.py, etc.) instead.")
    print("\nExample:")
    print("  python -m scrapers.fox")
    print("  python -m scrapers.paradise")
