import json
from datetime import datetime
from collections import defaultdict

# === Load JSON ===
with open("revue_films.json", "r", encoding="utf-8") as f:
    films = json.load(f)

# === Group by date ===
calendar = defaultdict(list)

for film in films:
    raw = film["showtime"]
    try:
        dt = datetime.strptime(raw, "%a %b %d, %I:%M %p")
    except:
        try:
            dt = datetime.strptime(raw, "%a %b %d, %H:%M %p")
        except:
            continue  # skip badly formatted

    date_key = dt.strftime("%A, %B %d")
    time_str = dt.strftime("%I:%M %p")
    calendar[date_key].append({
        "title": film["title"],
        "link": film["link"],
        "time": time_str
    })

# === Sort by date ===
sorted_days = sorted(calendar.items(), key=lambda x: datetime.strptime(x[0], "%A, %B %d"))

# === Generate HTML ===
html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Revue Cinema Schedule</title>
  <style>
    body { font-family: sans-serif; padding: 2rem; background: #f9f9f9; }
    h2 { border-bottom: 1px solid #ccc; padding-bottom: 5px; }
    .film { margin: 0.5rem 0; }
    .time { font-weight: bold; margin-right: 1rem; }
    a { text-decoration: none; color: #333; }
  </style>
</head>
<body>
  <h1>🎬 Revue Cinema Schedule</h1>
"""

for date, films_on_day in sorted_days:
    html += f"<h2>{date}</h2>\n"
    for film in sorted(films_on_day, key=lambda f: f["time"]):
        html += f"<div class='film'><span class='time'>{film['time']}</span><a href='{film['link']}' target='_blank'>{film['title']}</a></div>\n"

html += "</body></html>"

# === Save to HTML file ===
with open("revue_films.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Created revue_films.html — open it in your browser!")
