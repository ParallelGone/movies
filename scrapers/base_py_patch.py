# ============================================================
# ADD THIS CODE TO THE TOP OF YOUR base.py FILE
# (Right after all the import statements)
# ============================================================

import sys
import io

# Windows Unicode/Emoji Fix
# This prevents UnicodeEncodeError when printing emoji on Windows
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

# ============================================================
# EXAMPLE: Where to add this in your base.py
# ============================================================

"""
Your file should look like this:

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from pathlib import Path

# ← ADD THE UNICODE FIX HERE (paste the code above)

import sys
import io

if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass
    else:
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

# Then continue with your class definition:
class BaseScraper:
    def __init__(self, theater_name, theater_url):
        # ... rest of your code
"""

# ============================================================
# ALTERNATIVE: Safe Print Function
# ============================================================

# If the above doesn't work, add this function and use it instead of print()

def safe_print(message):
    """
    Print function that handles Unicode errors gracefully.
    Use this instead of print() in your scrapers.
    """
    try:
        print(message)
    except UnicodeEncodeError:
        # Strip emoji and special characters
        try:
            # Try to encode as ASCII, replacing bad characters
            cleaned = message.encode('ascii', errors='replace').decode('ascii')
            print(cleaned)
        except Exception:
            # If all else fails, print a placeholder
            print("[Output contains special characters that cannot be displayed]")

# Usage example:
# Instead of: print(f"📄 Loading page...")
# Use:        safe_print(f"📄 Loading page...")
