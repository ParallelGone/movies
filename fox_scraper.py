import json
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    driver.get("https://www.foxtheatre.ca/whats-on/now-showing/")
    print("📄 Page loaded")

    # Improved scrolling logic
    SCROLL_PAUSE_TIME = 2
    MAX_SCROLL_ATTEMPTS = 20
    last_height = driver.execute_script("return document.body.scrollHeight")
    same_height_count = 0

    for i in range(MAX_SCROLL_ATTEMPTS):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        print(f"🔄 Scroll attempt {i+1}, height: {new_height}")

        if new_height == last_height:
            same_height_count += 1
            if same_height_count >= 3:
                print("✅ Reached end of scrollable content")
                break
        else:
            same_height_count = 0
            last_height = new_height

    # Extract films
    films = []
    seen = set()
    blocks = driver.find_elements(By.CSS_SELECTOR, "div[data-element_type='container']")
    print(f"🔍 Processing {len(blocks)} blocks")

    for block in blocks:
        try:
            h4 = block.find_element(By.CSS_SELECTOR, "h4.elementor-heading-title")
            current_title = h4.text.strip()
        except:
            continue

        try:
            link_elem = block.find_element(By.CSS_SELECTOR, "a[href*='/movies/']")
            current_link = link_elem.get_attribute("href")
        except:
            current_link = "https://www.foxtheatre.ca/whats-on/now-showing/"

        spans = block.find_elements(By.CSS_SELECTOR, "span[data-date]")
        for span in spans:
            time_text = span.text.strip()
            raw_date = span.get_attribute("data-date")
            if ":" in time_text and ("am" in time_text.lower() or "pm" in time_text.lower()):
                try:
                    formatted_date = datetime.strptime(raw_date, "%Y-%m-%d").strftime("%A, %B %-d")
                except ValueError:
                    formatted_date = raw_date
                showtime = f"{formatted_date}, {time_text}"
                key = (current_title, showtime)
                if key not in seen:
                    seen.add(key)
                    films.append({
                        "title": current_title,
                        "showtime": showtime,
                        "link": current_link,
                        "source": "Fox Theatre"
                    })

    with open("fox_films.json", "w", encoding="utf-8") as f:
        json.dump(films, f, indent=2, ensure_ascii=False)

    print(f"✅ Done! Saved {len(films)} unique films to fox_films.json")

finally:
    print("👋 Closing browser")
    driver.quit()
