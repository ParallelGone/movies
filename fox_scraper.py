# fox_scraper.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_fox():
    url = "https://www.foxtheatre.ca/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    events = []

    schedule_items = soup.select("div.sqs-block-content h3")  # Each movie title is in an h3 tag inside .sqs-block-content
    for item in schedule_items:
        title = item.get_text(strip=True)
        if title and not title.lower().startswith("coming soon"):
            events.append({
                "title": title,
                "datetime": "TBD",
                "link": url  # There's not always a dedicated page, so just link to homepage for now
            })

    return events

if __name__ == "__main__":
    movies = scrape_fox()
    for movie in movies:
        print(f"{movie['datetime']} - {movie['title']}\n{movie['link']}\n")
