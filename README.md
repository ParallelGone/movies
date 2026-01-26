# 🎬 Toronto Rep Cinema Calendar

A scraping and calendar generation tool for Toronto's repertory and independent cinemas.

## Supported Theaters

| Theater | Website | Color |
|---------|---------|-------|
| **Revue Cinema** | revuecinema.ca | 🔵 Blue |
| **Paradise Theatre** | paradiseonbloor.com | 🟢 Green |
| **TIFF Bell Lightbox** | tiff.net | 🔴 Red |
| **Fox Theatre** | foxtheatre.ca | 🟠 Amber |
| **Kingsway Theatre** | kingswaymovies.ca | 🟣 Purple |

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd rep_cinema
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Chrome** (if not already installed) - Selenium requires Chrome browser.

## Usage

### Quick Start (Scrape All + Generate Calendar)

```bash
# Windows
update.bat

# Mac/Linux
./update.sh

# Or directly with Python
python main.py
```

### Command Line Options

```bash
# Scrape all theaters sequentially
python main.py

# Scrape all theaters in parallel (faster)
python main.py --parallel

# Scrape specific theaters only
python main.py --theaters fox revue tiff

# Only scrape, don't generate calendar
python main.py --scrape-only

# Only generate calendar from existing data
python main.py --generate-only

# Skip git push
python main.py --no-git

# Combine options
python main.py --theaters fox paradise --parallel --no-git
```

### Running Individual Scrapers

```bash
# Run a single scraper directly
python -m scrapers.fox
python -m scrapers.revue
python -m scrapers.paradise
python -m scrapers.tiff
python -m scrapers.kingsway
```

## Project Structure

```
rep_cinema/
├── config.py           # All configuration in one place
├── generator.py        # HTML calendar generator
├── main.py             # Main orchestration script
├── requirements.txt    # Python dependencies
├── update.bat          # Windows launcher
├── update.sh           # Mac/Linux launcher
├── scrapers/
│   ├── __init__.py     # Scraper registry
│   ├── base.py         # Base scraper class (shared logic)
│   ├── fox.py          # Fox Theatre scraper
│   ├── paradise.py     # Paradise Theatre scraper
│   ├── revue.py        # Revue Cinema scraper
│   ├── tiff.py         # TIFF Bell Lightbox scraper
│   └── kingsway.py     # Kingsway Theatre scraper
├── data/               # Generated JSON files
│   ├── fox_films.json
│   ├── paradise_films.json
│   ├── revue_films.json
│   ├── tiff_films.json
│   └── kingsway_films.json
└── index.html          # Generated calendar
```

## Adding a New Theater

1. **Add configuration in `config.py`:**
   ```python
   THEATERS = {
       # ... existing theaters ...
       "newtheater": {
           "name": "New Theater Name",
           "url": "https://newtheater.com/schedule",
           "color": "#hexcolor",
           "enabled": True,
       },
   }
   ```

2. **Create a new scraper in `scrapers/newtheater.py`:**
   ```python
   from .base import BaseScraper
   from config import THEATERS
   
   class NewTheaterScraper(BaseScraper):
       def __init__(self):
           config = THEATERS["newtheater"]
           super().__init__("newtheater", config["name"], config["url"])
           
       def scrape(self):
           # Your scraping logic here
           # Use self.add_film(title, showtime, link) to add films
           # Use inherited methods like scroll_to_load_all(), click_load_more()
           return self.films
   ```

3. **Register in `scrapers/__init__.py`:**
   ```python
   from .newtheater import NewTheaterScraper
   
   SCRAPER_REGISTRY = {
       # ... existing scrapers ...
       "newtheater": NewTheaterScraper,
   }
   ```

## Configuration Options

Edit `config.py` to customize:

- **BROWSER_OPTIONS**: Headless mode, browser settings
- **SCRAPE_SETTINGS**: Timeouts, retry attempts, scroll settings
- **OUTPUT_DIR**: Where JSON files are saved
- **HTML_OUTPUT**: Name of generated calendar file

## Troubleshooting

### Chrome/Selenium Issues
- Ensure Chrome is installed and up to date
- `webdriver-manager` should auto-download the correct ChromeDriver

### Scraper Fails for Specific Theater
- Website structure may have changed
- Check the browser console for errors
- Run with `--headless False` in config to see the browser

### Date Parsing Issues
- Some theaters use non-standard date formats
- Check the raw showtime strings in the JSON files

## GitHub Pages Deployment

The script can auto-push to GitHub Pages:

1. Set up your repository with GitHub Pages enabled
2. Run `python main.py` (without `--no-git`)
3. The calendar will be published automatically

## License

MIT License - Feel free to use and modify!
