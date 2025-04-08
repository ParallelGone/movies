from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
import time

CHROMEDRIVER_PATH = "D:/tools/chromedriver.exe"

options = Options()
# options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://paradiseonbloor.com/coming-soon/")
print("📄 Page loaded:", driver.title)
time.sleep(5)  # Wait for content to load

films = []

film_blocks = driver.find_elements(By.CLASS_NAME, "showtimes-description")
print(f"✅ Found {len(film_blocks)} film blocks")

for block in film_blocks:
    try:
        title_tag = block.find_element(By.CLASS_NAME, "show-title").find_element(By.TAG_NAME, "a")
        title = title_tag.text.strip()
        link = title_tag.get_attribute("href")
    except:
        title, link = "Untitled", None

    try:
        date_tag = block.find_element(By.CLASS_NAME, "selected-date")
        date = date_tag.text.strip().replace("\n", " ")
    except:
        date = "Unknown"

    try:
        time_tags = block.find_elements(By.CLASS_NAME, "showtime")
        times = [t.text.strip() for t in time_tags]
    except:
        times = []

    for t in times:
        films.append({
            "title": title,
            "link": link,
            "showtime": f"{date}, {t}",
            "source": "Paradise Theatre"
        })

driver.quit()

# Print result
for film in films:
    print(f"🎬 {film['title']}")
    print(f"🕒 {film['showtime']}")
    print(f"🔗 {film['link']}")
    print("-" * 40)

# Save to JSON
with open("paradise_films.json", "w", encoding="utf-8") as f:
    json.dump(films, f, indent=2, ensure_ascii=False)

print("💾 Saved to paradise_films.json")
