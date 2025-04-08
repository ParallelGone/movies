# royal_scraper.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_royal():
    url = "https://theroyal.to/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    events = []

    for event in soup.select(".views-row"):
        title_tag = event.select_one(".views-field-title a")
        date_tag = event.select_one(".date-display-single")

        if title_tag and date_tag:
            title = title_tag.text.strip()
            link = title_tag['href']
            datetime_str = date_tag['content'] if 'content' in date_tag.attrs else date_tag.text.strip()

            try:
                showtime = datetime.fromisoformat(datetime_str)
            except:
                showtime = datetime.now()  # fallback

            events.append({
                "title": title,
                "datetime": showtime,
                "link": f"https://theroyal.to{link}"
            })

    return events

if __name__ == "__main__":
    movies = scrape_royal()
    for movie in movies:
        print(f"{movie['datetime']} - {movie['title']}\n{movie['link']}\n")
