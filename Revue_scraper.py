from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time

# === SETUP ===
CHROMEDRIVER_PATH = "D:/tools/chromedriver.exe"  # <-- Update this if needed

options = Options()
# options.add_argument("--headless")  # Uncomment for headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

# === LOAD PAGE ===
driver.get("https://revuecinema.ca/films/")
print("📄 Page loaded:", driver.title)

# === CLICK "LOAD MORE" UNTIL DONE ===
max_clicks = 10
clicks = 0

while clicks < max_clicks:
    try:
        load_more = driver.find_element(By.XPATH, "//a[text()='Load More']")
        ActionChains(driver).move_to_element(load_more).perform()
        time.sleep(1)
        load_more.click()
        print("🔄 Clicked 'Load More'")
        time.sleep(3)  # Wait for new content to load
        clicks += 1
    except:
        print("✅ 'Load More' button not found or done loading.")
        break

# === SCRAPE FILM INFO ===
film_blocks = driver.find_elements(By.CLASS_NAME, "brxe-sdlpwn")
print(f"🎬 Found {len(film_blocks)} total films.\n")

films = []

for block in film_blocks:
    try:
        title_tag = block.find_element(By.TAG_NAME, "h5").find_element(By.TAG_NAME, "a")
        title = title_tag.text.strip()
        link = title_tag.get_attribute("href")
    except:
        title, link = "Untitled", None

    try:
        showtime_tag = block.find_element(By.CLASS_NAME, "brxe-ndxpjc")
        showtime = showtime_tag.text.strip()
    except:
        showtime = "No time listed"

    films.append({
        "title": title,
        "link": link,
        "showtime": showtime,
        "source": "Revue Cinema"
    })

driver.quit()

# === PRINT RESULTS (OPTIONAL) ===
for film in films:
    print(f"🎬 {film['title']}")
    print(f"🔗 {film['link']}")
    print(f"🕒 Showtime: {film['showtime']}")
    print("-" * 40)

# === SAVE TO JSON ===
with open("revue_films.json", "w", encoding="utf-8") as f:
    json.dump(films, f, indent=2, ensure_ascii=False)

print("💾 Saved film data to revue_films.json")
