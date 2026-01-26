"""
Configuration for Toronto Rep Cinema Calendar
All theater information in one place for easy maintenance.
"""

# Theater configuration - add new theaters here
THEATERS = {
    "revue": {
        "name": "Revue Cinema",
        "url": "https://revuecinema.ca/films/",
        "color": "#3b82f6",  # Blue
        "enabled": True,
    },
    "paradise": {
        "name": "Paradise Theatre",
        "url": "https://paradiseonbloor.com/coming-soon/",
        "color": "#10b981",  # Green
        "enabled": True,
    },
    "tiff": {
        "name": "TIFF Bell Lightbox",
        "url": "https://tiff.net/calendar",
        "color": "#ef4444",  # Red
        "enabled": True,
    },
    "fox": {
        "name": "Fox Theatre",
        "url": "https://www.foxtheatre.ca/whats-on/now-showing/",
        "color": "#f59e0b",  # Amber
        "enabled": True,
    },
    "kingsway": {
        "name": "Kingsway Theatre",
        "url": "http://kingswaymovies.ca/",
        "color": "#8b5cf6",  # Purple
        "enabled": True,
    },
}

# Selenium browser options
BROWSER_OPTIONS = {
    "headless": False,  # Set True for background operation
    "no_sandbox": True,
    "disable_dev_shm": True,
    "start_maximized": True,
}

# Scraping settings
SCRAPE_SETTINGS = {
    "page_load_wait": 5,          # Seconds to wait for page load
    "scroll_wait": 3,             # Seconds between scrolls
    "max_scroll_attempts": 20,    # Max scroll iterations
    "max_load_more_clicks": 10,   # Max "Load More" button clicks
    "retry_attempts": 3,          # Retries on failure
    "retry_delay": 5,             # Seconds between retries
}

# Output settings
OUTPUT_DIR = "data"
HTML_OUTPUT = "index.html"

# Date/time formats
DATE_FORMAT_DISPLAY = "%A, %B %d"  # "Monday, January 26" (use %#d on Windows for no zero-padding)
DATE_FORMAT_KEY = "%Y-%m-%d"        # "2026-01-26"
TIME_FORMAT = "%I:%M %p"            # "07:30 PM"
