
import json
from datetime import datetime
from collections import defaultdict
from dateutil import parser

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

revue = load_json("revue_films.json")
paradise = load_json("paradise_films.json")
tiff = load_json("tiff_films.json")

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

sorted_dates = sorted(date_map.keys())
sorted_months = sorted(months, key=lambda m: datetime.strptime(m, "%B %Y"))

theater_classes = {
    "Revue Cinema": "revue",
    "Paradise Theatre": "paradise",
    "TIFF Bell Lightbox": "tiff"
}

html = []
html.append("""<!DOCTYPE html><html lang='en'><head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Toronto Rep Cinema Calendar</title>
<style>
body { font-family: system-ui, sans-serif; padding: 1rem; margin: 0; background: #f9f9f9; color: #000; }
h1 { font-size: 1.5rem; margin-bottom: 1rem; text-align: center; }
h2 { font-size: 1.2rem; margin-top: 2rem; margin-bottom: 1rem; border-bottom: 1px solid #ccc; padding-bottom: 0.3rem; }
.filters { display: flex; flex-direction: column; align-items: center; gap: 0.5rem; margin-bottom: 1.5rem; }
.toggle-filters { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.toggle { padding: 0.4rem 1rem; font-size: 0.9rem; border-radius: 10px; border: none; color: white; cursor: pointer; font-weight: bold; }
.toggle.revue { background-color: #3b82f6; }
.toggle.paradise { background-color: #10b981; }
.toggle.tiff { background-color: #ef4444; }
.toggle.inactive { opacity: 0.4; }
.view-buttons { margin-bottom: 1rem; }
.view-buttons button { padding: 0.4rem 1rem; font-size: 1rem; margin: 0 0.3rem; cursor: pointer; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 1rem; }
.day-box, .list-day { background: white; border: 1px solid #ddd; border-radius: 0.5rem; padding: 1rem; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
.day-box h3, .list-day h2 { margin-top: 0; font-size: 1rem; color: #555; }
.film { margin: 0.5rem 0; line-height: 1.4; display: flex; align-items: center; gap: 0.5rem; }
.time { font-weight: bold; padding: 0.2rem 0.5rem; border-radius: 5px; color: white; font-size: 0.85rem; }
.revue .time { background-color: #3b82f6; }
.paradise .time { background-color: #10b981; }
.tiff .time { background-color: #ef4444; }
a { color: #000; text-decoration: none; font-weight: 500; }
a:hover { text-decoration: underline; }
.hidden { display: none; }
@media (max-width: 600px) { .grid { grid-template-columns: 1fr; } }
</style></head><body>
<h1>🎬 Toronto Rep Cinema Calendar</h1>
<div class='filters'>
  <label>🎭 Filter by Theater:</label>
  <div class='toggle-filters'>
    <button class='toggle tiff active' data-source='TIFF Bell Lightbox'>TIFF</button>
    <button class='toggle revue active' data-source='Revue Cinema'>REVUE</button>
    <button class='toggle paradise active' data-source='Paradise Theatre'>PARADISE</button>
  </div>
  <div class='view-buttons'>
    <button onclick="toggleView('grid-view')">🗓️ Grid View</button>
    <button onclick="toggleView('list-view')">📃 List View</button>
  </div>
</div>
<div id='grid-view'>""")



for month in sorted_months:
    html.append(f"<h2>{month}</h2><div class='grid'>")
    for date in sorted_dates:
        films = date_map[date]
        if not films or films[0]["month"] != month:
            continue
        html.append(f"<div class='day-box'><h3>{films[0]['readable']}</h3>")
        for film in sorted(films, key=lambda x: x["time"]):
            css = theater_classes.get(film["source"], "default")
            html.append(f"<div class='film {css}' data-source='{film['source']}'><span class='time'>{film['time']}</span><a href='{film['link']}' target='_blank'>{film['title']}</a></div>")
        html.append("</div>")
    html.append("</div>")

html.append("</div><div id='list-view' class='hidden'>")
for date in sorted_dates:
    films = date_map[date]
    html.append(f"<div class='list-day'><h2>{films[0]['readable']}</h2>")
    for film in sorted(films, key=lambda x: x["time"]):
        css = theater_classes.get(film["source"], "default")
        html.append(f"<div class='film {css}' data-source='{film['source']}'><span class='time'>{film['time']}</span><a href='{film['link']}' target='_blank'>{film['title']}</a></div>")
    html.append("</div>")
html.append("</div>")

html.append("""
<script>
const activeSources = new Set(["Revue Cinema", "Paradise Theatre", "TIFF Bell Lightbox"]);

function updateFilters() {
  document.querySelectorAll('.film').forEach(film => {
    const source = film.getAttribute('data-source');
    film.style.display = activeSources.has(source) ? 'flex' : 'none';
  });
  document.querySelectorAll('.day-box, .list-day').forEach(day => {
    const visible = day.querySelectorAll('.film:not([style*="display: none"])').length > 0;
    day.style.display = visible ? 'block' : 'none';
  });
}

function toggleFilter(button) {
  const source = button.getAttribute('data-source');
  if (activeSources.has(source)) {
    activeSources.delete(source);
    button.classList.remove('active');
    button.classList.add('inactive');
  } else {
    activeSources.add(source);
    button.classList.add('active');
    button.classList.remove('inactive');
  }
  updateFilters();
}

function toggleView(viewId) {
  document.getElementById('grid-view').classList.add('hidden');
  document.getElementById('list-view').classList.add('hidden');
  document.getElementById(viewId).classList.remove('hidden');
}

window.onload = function () {
  document.querySelectorAll('.toggle').forEach(btn => {
    btn.addEventListener('click', () => toggleFilter(btn));
  });
  toggleView('grid-view');
  updateFilters();
}
</script>
</body></html>""")

with open("index.html", "w", encoding="utf-8") as f:
    f.write("\n".join(html))

print("✅ Created index.html with color-coded times and toggles.")
