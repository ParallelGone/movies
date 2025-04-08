from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
import time

CHROMEDRIVER_PATH = "D:/tools/chromedriver.exe"  # Update this if needed

options = Options()
# options.add_argument("--headless")  # Uncomment for headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://tiff.net/calendar")
print("📄 TIFF Calendar loaded:", driver.title)

time.sleep(6)  # Allow Vue content to fully render

films = []

# Find daily sections on the calendar
day_sections = driver.find_elements(By.CLASS_NAME, "calendar-list-item")

print(f"✅ Found {len(day_sections)} calendar sections")

for section in day_sections:
    try:
        # Extract date text (e.g. "Today Apr 8" → "Apr 8")
        date_header = section.find_element(By.CLASS_NAME, "style__date___312bI").text.strip()
        parts = date_header.split()
        date_str = " ".join([p for p in parts if p not in ["Today", "Tomorrow"]])
    except:
        date_str = "Unknown Date"

    # Each film in the section
    title_cards = section.find_elements(By.CLASS_NAME, "style__cardTitle___3rkLd")

    for title_card in title_cards:
        try:
            title_tag = title_card.find_element(By.TAG_NAME, "a")
            title = title_tag.text.strip()
            if "Film Reference Library Public Hours" in title:
                continue  # skip this entry
            if "From Silence to Sound: Tuning the Auditory Experience" in title:
                continue  # skip this entry
            event_link = title_tag.get_attribute("href")
            full_event_link = f"https://tiff.net{event_link}" if event_link.startswith("/") else event_link
        except:
            title = "Untitled"
            full_event_link = None

        # Go up one level to find showtimes container
        try:
            parent = title_card.find_element(By.XPATH, "..")

            showtime_buttons = parent.find_elements(By.CLASS_NAME, "style__screeningButtonLink___kUNSA")

            for btn in showtime_buttons:
                try:
                    time_str = btn.find_element(By.CLASS_NAME, "style__screeningDisplayTime___2VUn1").text.strip()
                    ticket_link = btn.get_attribute("href")
                    full_showtime = f"{date_str}, {time_str}"

                    films.append({
                        "title": title,
                        "link": ticket_link,
                        "showtime": full_showtime,
                        "source": "TIFF Bell Lightbox"
                    })
                except:
                    continue

        except:
            continue

driver.quit()

# Save to JSON
with open("tiff_films.json", "w", encoding="utf-8") as f:
    json.dump(films, f, indent=2, ensure_ascii=False)

print(f"✅ Saved {len(films)} TIFF listings to tiff_films.json")
