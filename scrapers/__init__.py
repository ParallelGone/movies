"""
Scrapers package - contains all theater-specific scrapers.
"""

from .base import BaseScraper
from .fox import FoxScraper
from .paradise import ParadiseScraper
from .revue import RevueScraper
from .tiff import TiffScraper
from .kingsway import KingswayScraper

# Registry of all available scrapers
SCRAPER_REGISTRY = {
    "fox": FoxScraper,
    "paradise": ParadiseScraper,
    "revue": RevueScraper,
    "tiff": TiffScraper,
    "kingsway": KingswayScraper,
}

__all__ = [
    "BaseScraper",
    "FoxScraper",
    "ParadiseScraper", 
    "RevueScraper",
    "TiffScraper",
    "KingswayScraper",
    "SCRAPER_REGISTRY",
]
