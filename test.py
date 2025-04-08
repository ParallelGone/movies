import requests

URL = "https://revuecinema.ca/films/"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

res = requests.get(URL, headers=HEADERS)
print("Status Code:", res.status_code)
print("Content snippet:", res.text[:500])
