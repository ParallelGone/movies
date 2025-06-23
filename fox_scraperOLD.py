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

try:
    driver.get("https://www.foxtheatre.ca/whats-on/now-showing/")
    print("📄 Page loaded")

    # Scroll more aggressively by card count
    actions = ActionChains(driver)
    body = driver.find_element(By.TAG_NAME, "body")

    last_count = 0
    same_count = 0
    max_same_count = 5

    while same_count < max_same_count:
        cards = driver.find_elements(By.CSS_SELECTOR, "div[data-element_type='container']")
        driver.execute_script("window.scrollBy(0, 1000);")
        try:
            actions.move_to_element_with_offset(body, 10, 10).perform()
        except Exception as e:
            print(f"⚠️ move_to_element_with_offset failed: {e}")
        time.sleep(3)  # slightly longer wait
        new_count = len(driver.find_elements(By.CSS_SELECTOR, "div[data-element_type='container']"))
        print(f"🔄 Cards loaded: {new_count}")
        if new_count == last_count:
            same_count += 1
        else:
            same_count = 0
            last_count = new_count

    print("✅ Scrolling complete with", last_count, "containers")

    # Extract films
    films = []
    seen = set()
    blocks = driver.find_elements(By.CSS_SELECTOR, "div[data-element_type='container']")
    print(f"🔍 Processing {len(blocks)} blocks")

    current_title = None
    current_link = None

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

    with open("fox_films.json", "w", encoding="utf-8") as f:
        json.dump(films, f, indent=2, ensure_ascii=False)

    print(f"✅ Done! Saved {len(films)} unique films to fox_films.json")

finally:
    print("👋 Closing browser")
    driver.quit()