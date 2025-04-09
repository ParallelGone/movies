import json
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://www.foxtheatre.ca/whats-on/now-showing/")
print("📄 Page loaded")

# Scroll until fully loaded
actions = ActionChains(driver)
prev_height = 0
unchanged_scrolls = 0
while unchanged_scrolls < 6:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    actions.move_by_offset(0, 50).perform()
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == prev_height:
        unchanged_scrolls += 1
    else:
        unchanged_scrolls = 0
        prev_height = new_height

print("✅ Finished scrolling")

# Extract films
films = []
seen = set()  # for deduplication
blocks = driver.find_elements(By.CSS_SELECTOR, "div[data-element_type='container']")
print(f"🔍 Processing {len(blocks)} blocks")

current_title = None
current_link = None

for block in blocks:
    try:
        # Get title
        try:
            h4 = block.find_element(By.CSS_SELECTOR, "h4.elementor-heading-title")
            current_title = h4.text.strip()
        except:
            pass

        # Get link
        try:
            link_elem = block.find_element(By.CSS_SELECTOR, "a[href*='/movies/']")
            current_link = link_elem.get_attribute("href")
        except:
            current_link = "https://www.foxtheatre.ca/whats-on/now-showing/"

        # Times
        spans = block.find_elements(By.CSS_SELECTOR, "span[data-date]")
        for span in spans:
            time_text = span.text.strip()
            raw_date = span.get_attribute("data-date")
            if ":" in time_text and ("am" in time_text.lower() or "pm" in time_text.lower()):
                try:
                    formatted_date = datetime.strptime(raw_date, "%Y-%m-%d").strftime("%A, %B %-d")
                except ValueError:
                    formatted_date = raw_date
                if current_title:
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

    except Exception as e:
        print(f"⚠️ Skipped block due to error: {e}")
        continue

driver.quit()

# Save
with open("fox_films.json", "w", encoding="utf-8") as f:
    json.dump(films, f, indent=2, ensure_ascii=False)

print(f"✅ Done! Saved {len(films)} unique films to fox_films.json")