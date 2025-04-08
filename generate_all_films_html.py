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

# === Combine all ===
all_films = revue + paradise + tiff
calendar = defaultdict(list)

for film in all_films:
    raw = film["showtime"]
    title = film["title"]
    link = film["link"]
    source = film.get("source", "Unknown")

    try:
        dt = parser.parse(raw)
        date_key = dt.strftime("%A, %B %d")
        time_str = dt.strftime("%I:%M %p")
    except:
        date_key = "Unknown Date"
        time_str = raw

    calendar[date_key].append({
        "title": title,
        "link": link,
        "time": time_str,
        "source": source
    })

# === Sort by date ===
sorted_days = sorted(
    calendar.items(),
    key=lambda x: datetime.strptime(x[0], "%A, %B %d") if x[0] != "Unknown Date" else datetime.max
)

# === Map sources to CSS class names
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
  <title>Toronto Rep Cinema Calendar</title>
  <style>
    body { font-family: sans-serif; padding: 2rem; background: #f7f7f7; color: #333; }
    h1 { font-size: 2rem; margin-bottom: 1rem; }
    h2 { margin-top: 2rem; border-bottom: 1px solid #ccc; padding-bottom: 0.3rem; }
    .film { margin: 0.5rem 0; }
    .time { font-weight: bold; margin-right: 0.5rem; }
    .theater-label {
      display: inline-block;
      padding: 0.2rem 0.5rem;
      border-radius: 0.3rem;
      font-size: 0.85rem;
      font-weight: bold;
      margin-left: 0.5rem;
      color: white;
    }
    .theater-label.revue    { background-color: #3b82f6; }
    .theater-label.paradise { background-color: #10b981; }
    .theater-label.tiff     { background-color: #ef4444; }
    a { color: #333; text-decoration: none; }
    a:hover { text-decoration: underline; }

    .tabs {
      display: flex;
      gap: 1rem;
      margin-bottom: 1.5rem;
    }
    .tab {
      padding: 0.5rem 1rem;
      background: #eee;
      border-radius: 0.3rem;
      cursor: pointer;
      font-weight: bold;
    }
    .tab.active {
      background: #333;
      color: white;
    }
    .tab-content {
      display: none;
    }
    .tab-content.active {
      display: block;
    }
  </style>
  <script>
    function showTab(tabId) {
      const tabs = document.querySelectorAll('.tab');
      const contents = document.querySelectorAll('.tab-content');

      tabs.forEach(tab => tab.classList.remove('active'));
      contents.forEach(content => content.classList.remove('active'));

      document.getElementById(tabId).classList.add('active');
      document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    }

    window.onload = function() {
      showTab('all'); // default
    }
  </script>
</head>
<body>
  <h1>🎬 Toronto Rep Cinema Calendar</h1>

  <div class="tabs">
    <div class="tab active" data-tab="all" onclick="showTab('all')">All Theaters</div>
    <div class="tab" data-tab="revue" onclick="showTab('revue')">Revue Cinema</div>
    <div class="tab" data-tab="paradise" onclick="showTab('paradise')">Paradise Theatre</div>
    <div class="tab" data-tab="tiff" onclick="showTab('tiff')">TIFF Bell Lightbox</div>
  </div>
"""

# === Create separate content for each tab ===
tab_sources = ["all", "Revue Cinema", "Paradise Theatre", "TIFF Bell Lightbox"]

for tab in tab_sources:
    tab_id = tab.lower().split()[0] if tab != "all" else "all"
    html += f'<div class="tab-content" id="{tab_id}">\n'

    for date, films_on_day in sorted_days:
        films_for_tab = films_on_day if tab == "all" else [f for f in films_on_day if f["source"] == tab]
        if not films_for_tab:
            continue

        html += f"<h2>{date}</h2>\n"
        for film in sorted(films_for_tab, key=lambda f: f["time"]):
            source = film["source"]
            css_class = theater_classes.get(source, "default")
            html += (
                f"<div class='film'>"
                f"<span class='time'>{film['time']}</span>"
                f"<a href='{film['link']}' target='_blank'>{film['title']}</a>"
                f"<span class='theater-label {css_class}'>{source}</span>"
                f"</div>\n"
            )

    html += "</div>\n"

html += "</body></html>"

# === Save to HTML ===
with open("all_films.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Created all_films.html with tabs — open it in your browser!")
