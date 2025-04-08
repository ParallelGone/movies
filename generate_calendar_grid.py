import json
from datetime import datetime
from collections import defaultdict
from dateutil import parser

# === Load JSON files ===
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

revue = load_json("revue_films.json")
paradise = load_json("paradise_films.json")
tiff = load_json("tiff_films.json")

# === Combine and parse ===
all_films = revue + paradise + tiff
date_map = defaultdict(list)
months = set()

for film in all_films:
    raw = film["showtime"]
    try:
        dt = parser.parse(raw)
    except:
        continue

    date_key = dt.strftime("%Y-%m-%d")
    readable_date = dt.strftime("%A, %B %d")
    month_key = dt.strftime("%B %Y")
    time_str = dt.strftime("%I:%M %p")

    months.add(month_key)
    date_map[date_key].append({
        "readable": readable_date,
        "time": time_str,
        "title": film["title"],
        "link": film["link"],
        "source": film.get("source", "Unknown"),
        "month": month_key
    })

# === Sort data ===
sorted_dates = sorted(date_map.keys())
sorted_months = sorted(months, key=lambda m: datetime.strptime(m, "%B %Y"))

# === CSS-safe classes ===
theater_classes = {
    "Revue Cinema": "revue",
    "Paradise Theatre": "paradise",
    "TIFF Bell Lightbox": "tiff"
}

# === Build HTML ===
html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Rep Cinema Calendar</title>
  <style>
    body {
      font-family: system-ui, sans-serif;
      padding: 1rem;
      margin: 0;
      background: #f9f9f9;
      color: #333;
    }

    h1 {
      font-size: 1.5rem;
      margin-bottom: 1rem;
      text-align: center;
    }

    h2 {
      font-size: 1.2rem;
      margin-top: 2rem;
      margin-bottom: 1rem;
      border-bottom: 1px solid #ccc;
      padding-bottom: 0.3rem;
    }

    .controls {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      margin-bottom: 1rem;
      align-items: center;
    }

    .controls select,
    .controls button {
      font-size: 1rem;
      padding: 0.5rem 1rem;
      width: 100%;
      max-width: 300px;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
      gap: 1rem;
    }

    .day-box, .list-day {
      background: white;
      border: 1px solid #ddd;
      border-radius: 0.5rem;
      padding: 1rem;
      box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }

    .day-box h3, .list-day h2 {
      margin-top: 0;
      font-size: 1rem;
      color: #555;
    }

    .film {
      margin: 0.5rem 0;
      line-height: 1.4;
    }

    .time {
      font-weight: bold;
      margin-right: 0.5rem;
    }

    .label {
      display: inline-block;
      padding: 0.2rem 0.5rem;
      border-radius: 0.3rem;
      font-size: 0.8rem;
      font-weight: bold;
      color: white;
      margin-top: 0.2rem;
    }

    .revue { background-color: #3b82f6; }
    .paradise { background-color: #10b981; }
    .tiff { background-color: #ef4444; }

    a {
      color: #333;
      text-decoration: none;
    }

    a:hover {
      text-decoration: underline;
    }

    .hidden {
      display: none;
    }

    @media (max-width: 600px) {
      .grid {
        grid-template-columns: 1fr;
      }
    }
  </style>

  <script>
    function filterTheater(theater) {
      document.querySelectorAll('.film').forEach(film => {
        const source = film.getAttribute('data-source');
        film.style.display = (theater === 'all' || source === theater) ? 'block' : 'none';
      });

      document.querySelectorAll('.day-box, .list-day').forEach(day => {
        const visible = day.querySelectorAll('.film:not([style*="display: none"])').length > 0;
        day.style.display = visible ? 'block' : 'none';
      });
    }

    function toggleView(viewId) {
      document.getElementById('grid-view').classList.add('hidden');
      document.getElementById('list-view').classList.add('hidden');
      document.getElementById(viewId).classList.remove('hidden');
    }

    window.onload = function() {
      toggleView('grid-view');
    }
  </script>
</head>
<body>
  <h1>🎬 Toronto Rep Cinema Calendar</h1>
  <div class="controls">
    <label for="filter">🎭 Filter by Theater:</label>
    <select id="filter" onchange="filterTheater(this.value)">
      <option value="all">All Theaters</option>
      <option value="Revue Cinema">Revue Cinema</option>
      <option value="Paradise Theatre">Paradise Theatre</option>
      <option value="TIFF Bell Lightbox">TIFF Bell Lightbox</option>
    </select>

    <div class="toggle-btns">
      <button onclick="toggleView('grid-view')">🗓️ Grid View</button>
      <button onclick="toggleView('list-view')">📃 List View</button>
    </div>
  </div>
"""

# === Grid view ===
html += "<div id='grid-view'>\n"
for month in sorted_months:
    html += f"<h2>{month}</h2>\n"
    html += "<div class='grid'>\n"
    for date in sorted_dates:
        films = date_map[date]
        if not films or films[0]["month"] != month:
            continue
        html += f"<div class='day-box'>"
        html += f"<h3>{films[0]['readable']}</h3>"
        for film in sorted(films, key=lambda x: x["time"]):
            css = theater_classes.get(film["source"], "default")
            html += (
                f"<div class='film' data-source='{film['source']}'>"
                f"<span class='time'>{film['time']}</span>"
                f"<a href='{film['link']}' target='_blank'>{film['title']}</a><br>"
                f"<span class='label {css}'>{film['source']}</span>"
                f"</div>"
            )
        html += "</div>\n"
    html += "</div>\n"
html += "</div>\n"

# === List view ===
html += "<div id='list-view' class='hidden'>\n"
for date in sorted_dates:
    films = date_map[date]
    html += f"<div class='list-day'><h2>{films[0]['readable']}</h2>\n"
    for film in sorted(films, key=lambda x: x["time"]):
        css = theater_classes.get(film["source"], "default")
        html += (
            f"<div class='film' data-source='{film['source']}'>"
            f"<span class='time'>{film['time']}</span>"
            f"<a href='{film['link']}' target='_blank'>{film['title']}</a>"
            f"<span class='label {css}'>{film['source']}</span>"
            f"</div>\n"
        )
    html += "</div>\n"
html += "</div>\n"

# === Close and save ===
html += "</body></html>"

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Created calendar_grid.html with grid + list toggle and filter — open it in your browser!")
