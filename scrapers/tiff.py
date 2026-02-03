"""
TIFF Bell Lightbox scraper - Vue.js/React calendar interface.

Updated to handle CSS Module hash changes using partial class matching.
The TIFF site uses React with CSS Modules, so class names have random suffixes
like 'style__cardTitle___3rkLd' that change on each build.
"""

import re
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from .base import BaseScraper

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import THEATERS


class TiffScraper(BaseScraper):
    """Scraper for TIFF Bell Lightbox (tiff.net/calendar)"""
    
    # CSS Selectors using partial matching to survive CSS Module hash changes
    SELECTORS = {
        'date_group': '.calendar-list-item',
        'date_header': 'h2[class*="date"]',
        'movie_list': 'ul',
        'movie_item': 'li',
        'result_card': '[class*="resultCard"]',
        'card_title': '[class*="cardTitle"]',
        'card_directors': '[class*="cardDirectors"]',
        'programme_links': '[class*="programmeLinks"]',
        'ticketed_showtime': 'a[class*="screeningButtonLink"]',
        'free_showtime': '[class*="freeDropIn"]',
    }
    
    def __init__(self):
        config = THEATERS["tiff"]
        super().__init__("tiff", config["name"], config["url"])
        
    def load_page(self, wait_time=None) -> bool:
        """Override with longer wait for React rendering.

        IMPORTANT: must return a bool so BaseScraper.run() knows whether to continue.
        """
        ok = super().load_page()
        if not ok:
            return False

        # BaseScraper.load_page() is intentionally minimal; TIFF needs extra render time.
        import time
        time.sleep(wait_time or 20)

        try:
            # Wait for React to render date groups
            wait = WebDriverWait(self.driver, 45)
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, self.SELECTORS['date_group'])
            ))

            # Additional wait for result cards to render
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, self.SELECTORS['result_card'])
            ))

            print(f"🎬 [{self.theater_name}] React app loaded successfully")
            return True
        except Exception as e:
            print(f"❌ [{self.theater_name}] React calendar did not render: {e}")
            return False
    
    def _convert_date(self, date_text: str) -> str:
        """
        Convert TIFF date formats to standardized format.
        
        TIFF uses formats like:
        - "Today Jan 26"
        - "Tomorrow Jan 27"  
        - "Monday Jan 28"
        - "Tuesday Jan 29"
        
        We need to convert these to full date format:
        - "Monday, January 26"
        - "Tuesday, January 27"
        
        Args:
            date_text: Date string from TIFF website
            
        Returns:
            Formatted date string like "Monday, January 26"
        """
        if not date_text:
            return ""
        
        # Handle "Today" and "Tomorrow"
        today = datetime.now()
        
        if date_text.startswith("Today"):
            target_date = today
        elif date_text.startswith("Tomorrow"):
            target_date = today + timedelta(days=1)
        else:
            # Try to parse date like "Monday Jan 27" or "Monday, Jan 27"
            # Extract the month and day
            match = re.search(r'(\w+)\s+(\d{1,2})', date_text)
            if match:
                month_abbr = match.group(1)
                day = int(match.group(2))
                
                # Map month abbreviations
                month_map = {
                    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
                    'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
                    'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                }
                
                month = month_map.get(month_abbr, today.month)
                
                # Determine the year (handle year rollover)
                year = today.year
                if month < today.month or (month == today.month and day < today.day):
                    year += 1
                
                try:
                    target_date = datetime(year, month, day)
                except ValueError:
                    # Invalid date, return original
                    return date_text
            else:
                # Couldn't parse, return original
                return date_text
        
        # Format as "Monday, January 26"
        return target_date.strftime("%A, %B %-d" if os.name != 'nt' else "%A, %B %d").replace(" 0", " ")
        
    def _extract_time(self, text: str) -> str:
        """
        Extract time from text.
        
        Handles formats like "6:00pm", "12:30PM", "6:00pm open_in_new"
        
        Args:
            text: Text containing the time
            
        Returns:
            Formatted time string (e.g., "6:00PM") or empty string
        """
        if not text:
            return ""
            
        text = text.strip().lower()
        
        # Use regex to extract time
        match = re.search(r'(\d{1,2}:\d{2})\s*(am|pm)', text, re.IGNORECASE)
        if match:
            time_part = match.group(1)
            suffix = match.group(2).upper()
            return f"{time_part}{suffix}"
            
        return ""
    
    def _safe_get_text(self, parent, selector: str) -> str:
        """Safely get text content from an element."""
        try:
            element = parent.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip() if element.text else ""
        except NoSuchElementException:
            return ""
    
    def _safe_get_attribute(self, parent, selector: str, attribute: str) -> str:
        """Safely get an attribute from an element."""
        try:
            element = parent.find_element(By.CSS_SELECTOR, selector)
            return element.get_attribute(attribute) or ""
        except NoSuchElementException:
            return ""
        
    def scrape(self):
        """Main scraping logic."""
        # Get all date groups
        date_groups = self.driver.find_elements(
            By.CSS_SELECTOR, self.SELECTORS['date_group']
        )
        
        print(f"🎬 [{self.theater_name}] Found {len(date_groups)} date groups")
        
        for group in date_groups:
            # Extract date from header
            date_text = self._safe_get_text(group, self.SELECTORS['date_header'])
            if not date_text:
                date_text = "Unknown Date"
            
            # Convert to standard format
            formatted_date = self._convert_date(date_text)
            
            # Find movie list within this date group
            try:
                movie_list = group.find_element(
                    By.CSS_SELECTOR, self.SELECTORS['movie_list']
                )
            except NoSuchElementException:
                continue
                
            # Get all movie items
            movie_items = movie_list.find_elements(
                By.CSS_SELECTOR, self.SELECTORS['movie_item']
            )
            
            for item in movie_items:
                # Find the result card
                try:
                    card = item.find_element(
                        By.CSS_SELECTOR, self.SELECTORS['result_card']
                    )
                except NoSuchElementException:
                    continue
                
                # Extract event details
                title = self._safe_get_text(card, self.SELECTORS['card_title'])
                if not title:
                    continue  # Skip if no title
                    
                director = self._safe_get_text(card, self.SELECTORS['card_directors'])
                if director:
                    title = f"{title} - {director}"
                
                # Get event URL from title link
                event_url = self._safe_get_attribute(
                    card, 
                    f"{self.SELECTORS['card_title']} a", 
                    'href'
                )
                
                # Default link if no specific event URL
                link = event_url if event_url else self.url
                
                # Extract showtimes
                showtimes_found = []
                
                # Ticketed showtimes
                try:
                    ticketed_buttons = card.find_elements(
                        By.CSS_SELECTOR, self.SELECTORS['ticketed_showtime']
                    )
                    for btn in ticketed_buttons:
                        # Try to get time from span first, then full text
                        try:
                            span = btn.find_element(By.CSS_SELECTOR, 'span')
                            time_text = span.text
                        except NoSuchElementException:
                            time_text = btn.text
                            
                        time = self._extract_time(time_text)
                        if time:
                            ticket_link = btn.get_attribute('href')
                            showtimes_found.append({
                                'time': time,
                                'link': ticket_link or link
                            })
                except NoSuchElementException:
                    pass
                
                # Free/drop-in showtimes
                try:
                    free_slots = card.find_elements(
                        By.CSS_SELECTOR, self.SELECTORS['free_showtime']
                    )
                    for slot in free_slots:
                        time = self._extract_time(slot.text)
                        if time:
                            showtimes_found.append({
                                'time': f"{time} (Free)",
                                'link': link
                            })
                except NoSuchElementException:
                    pass
                
                # Add entry for each showtime (or one entry if no showtimes)
                if showtimes_found:
                    for showtime_data in showtimes_found:
                        showtime_str = f"{formatted_date}, {showtime_data['time']}"
                        self.add_film(title, showtime_str, showtime_data['link'])
                else:
                    # Add event without showtime (like exhibitions, etc.)
                    self.add_film(title, formatted_date, link)
                
        # If TIFF's site hides "today" once showtimes have passed, we still want
        # the calendar to include today's TIFF entries until the nightly run.
        # So: if we scraped zero items for today's date, merge in any existing
        # saved entries for today from the previous tiff_films.json.
        try:
            from datetime import datetime
            from zoneinfo import ZoneInfo
            today_str = datetime.now(ZoneInfo("America/Toronto")).strftime("%A, %B %-d").replace(" 0", " ")

            def _date_part(showtime: str) -> str:
                parts = (showtime or "").split(',')
                if len(parts) >= 2:
                    return ','.join(parts[:-1]).strip()
                # no time part
                return (showtime or "").strip()

            has_today = any(_date_part(f.get('showtime','')) == today_str for f in self.films)
            if not has_today and self.output_file.exists():
                import json
                with open(self.output_file, "r", encoding="utf-8") as f:
                    old = json.load(f)

                keep = [x for x in old if _date_part(x.get('showtime','')) == today_str]
                if keep:
                    seen = set((x.get('title',''), x.get('showtime','')) for x in self.films)
                    for x in keep:
                        key = (x.get('title',''), x.get('showtime',''))
                        if key not in seen:
                            self.films.append(x)
                            seen.add(key)
                    print(f"🧩 [{self.theater_name}] TIFF site omitted today; merged {len(keep)} saved entries for {today_str}")
        except Exception as e:
            print(f"⚠️  [{self.theater_name}] Could not merge today's TIFF entries: {e}")

        return self.films


if __name__ == "__main__":
    scraper = TiffScraper()
    films = scraper.run()
    print(f"\n🎬 Total films/screenings scraped: {len(films)}")
