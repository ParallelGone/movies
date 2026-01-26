"""
Kingsway Theatre scraper - parses showtime info from image alt/title text.
The Kingsway website uses an old-style format where showtimes are embedded
in image attributes like: "Film Title Fri/Mon to Thurs 1:00 pm / daily 7:00 pm"
"""

import re
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from .base import BaseScraper

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import THEATERS

# Day name mappings
DAY_MAP = {
    'mon': 0, 'monday': 0,
    'tue': 1, 'tues': 1, 'tuesday': 1,
    'wed': 2, 'wednesday': 2,
    'thu': 3, 'thur': 3, 'thurs': 3, 'thursday': 3,
    'fri': 4, 'friday': 4,
    'sat': 5, 'saturday': 5,
    'sun': 6, 'sunday': 6,
}

# Time pattern: captures "1:00 pm", "7:00 PM", etc.
TIME_PATTERN = re.compile(r'(\d{1,2}:\d{2}\s*(?:am|pm))', re.IGNORECASE)

# Day pattern: captures day names
DAY_PATTERN = re.compile(r'\b(mon|tues?|wed|thurs?|fri|sat|sun|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', re.IGNORECASE)


class KingswayScraper(BaseScraper):
    """Scraper for Kingsway Theatre (kingswaymovies.ca)"""
    
    def __init__(self):
        config = THEATERS["kingsway"]
        super().__init__("kingsway", config["name"], config["url"])
        
    def parse_schedule_text(self, text: str) -> list:
        """
        Parse schedule text like "Fri/Mon to Thurs 1:00 pm / daily 7:00 pm"
        Returns list of (day_indices, time_str) tuples.
        
        Key insight: "/" between day names (like "Fri/Mon") means OR, not a separator.
        We only split on "/" when it separates distinct time blocks.
        """
        schedules = []
        
        # Smart split: only split on "/" when followed by "daily" or a time pattern
        # This preserves "Fri/Mon" as a unit while splitting "1:00 pm / daily 7:00 pm"
        parts = re.split(r'\s*/\s*(?=daily|\d{1,2}:\d{2})', text, flags=re.IGNORECASE)
        
        for part in parts:
            times = TIME_PATTERN.findall(part)
            if not times:
                continue
                
            # Check for "daily" keyword
            if 'daily' in part.lower():
                # All days of the week
                for time_str in times:
                    schedules.append((list(range(7)), time_str))
                continue
                
            # Find day references (handle "/" between days as OR)
            # First, expand any day/day patterns
            expanded_part = part
            day_indices = set()
            
            # Handle "Mon to Thurs" ranges first
            range_matches = list(re.finditer(
                r'(\w+)\s+to\s+(\w+)', 
                expanded_part, 
                re.IGNORECASE
            ))
            for range_match in range_matches:
                start_day = range_match.group(1).lower()
                end_day = range_match.group(2).lower()
                
                if start_day in DAY_MAP and end_day in DAY_MAP:
                    start_idx = DAY_MAP[start_day]
                    end_idx = DAY_MAP[end_day]
                    
                    # Handle week wraparound
                    if start_idx <= end_idx:
                        day_indices.update(range(start_idx, end_idx + 1))
                    else:
                        day_indices.update(range(start_idx, 7))
                        day_indices.update(range(0, end_idx + 1))
            
            # Handle "/" between day names (e.g., "Fri/Mon", "Sat/Sun")
            # These are additional days, not separators
            day_slash_pattern = re.compile(
                r'((?:mon|tues?|wed|thurs?|fri|sat|sun|monday|tuesday|wednesday|thursday|friday|saturday|sunday)(?:\s*/\s*(?:mon|tues?|wed|thurs?|fri|sat|sun|monday|tuesday|wednesday|thursday|friday|saturday|sunday))*)',
                re.IGNORECASE
            )
            day_groups = day_slash_pattern.findall(part)
            for group in day_groups:
                # Split by "/" to get individual days
                individual_days = re.split(r'\s*/\s*', group)
                for day_name in individual_days:
                    day_lower = day_name.lower().strip()
                    if day_lower in DAY_MAP:
                        day_indices.add(DAY_MAP[day_lower])
            
            # Also find any standalone day names not caught above
            all_days = DAY_PATTERN.findall(part)
            for day_name in all_days:
                day_lower = day_name.lower()
                if day_lower in DAY_MAP:
                    day_indices.add(DAY_MAP[day_lower])
                        
            if day_indices:
                for time_str in times:
                    schedules.append((sorted(list(day_indices)), time_str))
            else:
                # No days specified, assume daily
                for time_str in times:
                    schedules.append((list(range(7)), time_str))
                    
        return schedules
        
    def expand_to_dates(self, day_indices: list, time_str: str, weeks_ahead: int = 2) -> list:
        """
        Expand day indices to actual dates for the next N weeks.
        Returns list of formatted showtime strings.
        """
        showtimes = []
        today = datetime.now().date()
        
        for day_offset in range(weeks_ahead * 7):
            target_date = today + timedelta(days=day_offset)
            
            if target_date.weekday() in day_indices:
                date_str = target_date.strftime("%A, %B %d").replace(" 0", " ")
                showtimes.append(f"{date_str}, {time_str}")
                
        return showtimes
        
    def extract_title_from_alt(self, alt_text: str) -> str:
        """
        Extract movie title from alt text.
        Title is typically at the beginning, before day/time info.
        """
        # Remove common suffixes
        text = alt_text.strip()
        
        # Find where the schedule info starts
        # Look for day names, "daily", or time patterns
        schedule_start = len(text)
        
        # Check for day names
        day_match = DAY_PATTERN.search(text)
        if day_match:
            schedule_start = min(schedule_start, day_match.start())
            
        # Check for "daily"
        daily_match = re.search(r'\bdaily\b', text, re.IGNORECASE)
        if daily_match:
            schedule_start = min(schedule_start, daily_match.start())
            
        # Check for time patterns
        time_match = TIME_PATTERN.search(text)
        if time_match:
            schedule_start = min(schedule_start, time_match.start())
            
        title = text[:schedule_start].strip()
        
        # Clean up title
        title = re.sub(r'\s+', ' ', title)  # Normalize whitespace
        title = title.rstrip(' -/')  # Remove trailing separators
        
        return title
        
    def scrape(self):
        # Find all images that might contain movie info
        images = self.driver.find_elements(By.TAG_NAME, "img")
        print(f"🔍 [{self.theater_name}] Checking {len(images)} images")
        
        seen = set()
        
        for img in images:
            # Get alt text or title
            alt_text = img.get_attribute("alt") or img.get_attribute("title") or ""
            
            if not alt_text:
                continue
                
            # Skip non-movie images (headers, logos, etc.)
            skip_keywords = ['kingsway theatre', 'twitter', 'facebook', 'logo', 'header']
            if any(kw in alt_text.lower() for kw in skip_keywords):
                continue
                
            # Check if this looks like a movie listing (has time info)
            if not TIME_PATTERN.search(alt_text):
                continue
                
            # Extract title and schedule
            title = self.extract_title_from_alt(alt_text)
            if not title or len(title) < 2:
                continue
                
            schedules = self.parse_schedule_text(alt_text)
            
            # Try to get a link from parent element
            link = self.url
            try:
                parent = img.find_element(By.XPATH, "./..")
                if parent.tag_name == "a":
                    link = parent.get_attribute("href") or self.url
            except Exception:
                pass
                
            # Expand schedules to actual dates
            for day_indices, time_str in schedules:
                showtimes = self.expand_to_dates(day_indices, time_str)
                
                for showtime in showtimes:
                    key = (title, showtime)
                    if key not in seen:
                        seen.add(key)
                        self.add_film(title, showtime, link)
                        
        return self.films


if __name__ == "__main__":
    scraper = KingswayScraper()
    films = scraper.run()
    print(f"\n🎬 Total films scraped: {len(films)}")
