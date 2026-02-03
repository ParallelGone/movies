"""
HTML Calendar Generator for Toronto Rep Cinema Calendar

Loads scraped film data and generates an interactive HTML calendar
with proper chronological sorting.
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from zoneinfo import ZoneInfo


# Configuration
DATA_DIR = "data"
HTML_OUTPUT = "index.html"

THEATERS = {
    "revue": {"name": "Revue Cinema", "color": "#3b82f6"},
    "paradise": {"name": "Paradise Theatre", "color": "#10b981"},
    "tiff": {"name": "TIFF Bell Lightbox", "color": "#ef4444"},
    "fox": {"name": "Fox Theatre", "color": "#f59e0b"},
    "kingsway": {"name": "Kingsway Theatre", "color": "#8b5cf6"},
}


def parse_time_for_sorting(showtime_str: str) -> int:
    """
    Extract time from showtime string and convert to minutes since midnight.
    
    This enables proper chronological sorting (12:00 PM before 10:00 PM).
    
    Args:
        showtime_str: Full showtime like "Monday, January 26, 3:45 PM"
        
    Returns:
        Minutes since midnight (0-1439) for sorting
    """
    # Extract time portion with regex
    time_match = re.search(r'(\d{1,2}):(\d{2})\s*(AM|PM)', showtime_str, re.IGNORECASE)
    
    if not time_match:
        return 0  # Default to midnight if can't parse
    
    hours = int(time_match.group(1))
    minutes = int(time_match.group(2))
    am_pm = time_match.group(3).upper()
    
    # Convert to 24-hour format
    if am_pm == 'PM' and hours != 12:
        hours += 12
    elif am_pm == 'AM' and hours == 12:
        hours = 0
    
    # Return total minutes since midnight
    return hours * 60 + minutes


def load_all_films() -> List[Dict]:
    """Load all film data from JSON files in the data directory."""
    all_films = []
    
    for theater_id in THEATERS.keys():
        json_file = os.path.join(DATA_DIR, f"{theater_id}_films.json")
        
        if not os.path.exists(json_file):
            print(f"⚠️  Warning: {json_file} not found, skipping...")
            continue
            
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                films = json.load(f)
                all_films.extend(films)
                print(f"✅ Loaded {len(films)} films from {theater_id}")
        except Exception as e:
            print(f"❌ Error loading {json_file}: {e}")
            
    return all_films


def normalize_date(date_str: str) -> str:
    """
    Normalize date strings to a standard format: "Monday, January 26"
    
    Handles various input formats:
    - "Today, Jan 26" → "Monday, January 26"
    - "Tomorrow, Jan 27" → "Tuesday, January 27"
    - "Tue, Jan 27" → "Tuesday, January 27"
    - "Tue Jan 27" → "Tuesday, January 27"
    - "Tuesday, January 27" → "Tuesday, January 27" (already normalized)
    
    Args:
        date_str: Date string in any format
        
    Returns:
        Normalized date string
    """
    # Day name mappings
    day_map = {
        'Mon': 'Monday', 'Tue': 'Tuesday', 'Wed': 'Wednesday', 'Thu': 'Thursday',
        'Fri': 'Friday', 'Sat': 'Saturday', 'Sun': 'Sunday',
        'Monday': 'Monday', 'Tuesday': 'Tuesday', 'Wednesday': 'Wednesday',
        'Thursday': 'Thursday', 'Friday': 'Friday', 'Saturday': 'Saturday', 'Sunday': 'Sunday'
    }
    
    # Month name mappings
    month_map = {
        'Jan': 'January', 'Feb': 'February', 'Mar': 'March', 'Apr': 'April',
        'May': 'May', 'Jun': 'June', 'Jul': 'July', 'Aug': 'August',
        'Sep': 'September', 'Oct': 'October', 'Nov': 'November', 'Dec': 'December',
        'January': 'January', 'February': 'February', 'March': 'March', 'April': 'April',
        'June': 'June', 'July': 'July', 'August': 'August',
        'September': 'September', 'October': 'October', 'November': 'November', 'December': 'December'
    }
    
    # Remove leading/trailing whitespace and commas
    date_str = date_str.strip().rstrip(',').strip()
    
    # Handle "Today" and "Tomorrow" relative dates
    today = datetime.now()
    
    if date_str.startswith("Today"):
        # Extract month and day if present: "Today, Jan 26"
        match = re.search(r'Today,?\s+(\w+)\s+(\d+)', date_str)
        if match:
            # Use today's date
            target_date = today
        else:
            target_date = today
        # Format as standard date
        day_name = target_date.strftime("%A")
        month_name = target_date.strftime("%B")
        day_num = target_date.strftime("%d").lstrip('0')
        return f"{day_name}, {month_name} {day_num}"
        
    elif date_str.startswith("Tomorrow"):
        # Extract month and day if present: "Tomorrow, Jan 27"
        match = re.search(r'Tomorrow,?\s+(\w+)\s+(\d+)', date_str)
        if match:
            # Use tomorrow's date
            target_date = today + timedelta(days=1)
        else:
            target_date = today + timedelta(days=1)
        # Format as standard date
        day_name = target_date.strftime("%A")
        month_name = target_date.strftime("%B")
        day_num = target_date.strftime("%d").lstrip('0')
        return f"{day_name}, {month_name} {day_num}"
    
    # Try to match pattern: "Day Month DD" or "Day, Month DD"
    # Examples: "Tue Jan 27", "Tue, Jan 27", "Tuesday, January 27"
    match = re.match(r'(\w+),?\s+(\w+)\s+(\d+)', date_str)
    
    if match:
        day_abbr = match.group(1)
        month_abbr = match.group(2)
        day_num = match.group(3)
        
        # Convert to full names
        day_full = day_map.get(day_abbr, day_abbr)
        month_full = month_map.get(month_abbr, month_abbr)
        
        # Strip leading zeros from day number (01 → 1)
        day_num = str(int(day_num))
        
        return f"{day_full}, {month_full} {day_num}"
    
    # If no match, return as-is
    return date_str


def extract_date(showtime: str) -> str:
    """
    Extract and normalize the date portion from a showtime string.
    
    Handles formats like:
    - "Monday, January 26, 3:45 PM" → "Monday, January 26"
    - "Tue, Jan 27, 6:30 pm" → "Tuesday, January 27"
    - "Tue Jan 27, 07:00 PM" → "Tuesday, January 27"
    
    Args:
        showtime: Full showtime string
        
    Returns:
        Normalized date portion of the showtime
    """
    # Split by comma and take all parts except the last (which is the time)
    parts = showtime.split(',')
    if len(parts) >= 2:
        # Join all parts except the last one (time part)
        date_part = ','.join(parts[:-1]).strip()
        # Normalize the date format
        return normalize_date(date_part)
    
    # For formats without comma like "Tue Jan 27 07:00 PM"
    # Extract just the date part (first 3 words)
    words = showtime.split()
    if len(words) >= 3:
        date_part = ' '.join(words[:3])
        return normalize_date(date_part)
    
    return normalize_date(showtime)


def date_to_obj(date_str: str, tz: str = "America/Toronto"):
    """Convert a normalized date string like "Monday, January 26" into a date object.

    We infer the year based on the current date in the given timezone.
    """
    # Expect: "<DayName>, <MonthName> <Day>"
    m = re.search(r'^\w+,\s+(\w+)\s+(\d{1,2})$', date_str.strip())
    if not m:
        return None

    month_name = m.group(1)
    day_num = int(m.group(2))

    month_order = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    month = month_order.get(month_name)
    if not month:
        return None

    now = datetime.now(ZoneInfo(tz)).date()
    year = now.year

    # Handle year rollover for schedules that span Dec -> Jan
    # If the month is "far behind" the current month, assume next year.
    if month < now.month and (now.month - month) >= 6:
        year += 1

    try:
        return datetime(year, month, day_num).date()
    except ValueError:
        return None


def extract_time(showtime: str) -> str:
    """
    Extract just the time portion from a showtime string.
    
    Args:
        showtime: Full showtime string like "Monday, January 26, 3:45 PM"
        
    Returns:
        Time string like "3:45 PM"
    """
    # Extract time with regex
    time_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)(?:\s*\([^)]+\))?)', showtime)
    if time_match:
        return time_match.group(1).strip()
    
    # Fallback: take last part after comma
    parts = showtime.split(',')
    if parts:
        return parts[-1].strip()
    
    return showtime


def parse_and_organize_films(all_films: List[Dict]) -> Tuple[Dict, List[Tuple]]:
    """
    Organize films by date and sort them chronologically.
    
    Args:
        all_films: List of film dictionaries
        
    Returns:
        Tuple of (date_map, sorted_months) where:
        - date_map: Dict mapping date strings to sorted lists of films
        - sorted_months: List of (month_name, year) tuples in chronological order
    """
    # Group films by date
    date_map = defaultdict(list)

    # Always exclude past dates (based on Toronto local date)
    today = datetime.now(ZoneInfo("America/Toronto")).date()
    dropped = 0

    for film in all_films:
        date_str = extract_date(film['showtime'])
        date_obj = date_to_obj(date_str)

        # If we can parse the date, enforce: date >= today
        if date_obj and date_obj < today:
            dropped += 1
            continue

        date_map[date_str].append(film)
    
    # Sort films within each day by time (CRITICAL FIX!)
    for date in date_map:
        date_map[date].sort(key=lambda f: parse_time_for_sorting(f['showtime']))
    
    # Extract and sort unique months
    month_set = set()
    for date_str in date_map.keys():
        date_obj = date_to_obj(date_str)
        if date_obj:
            month_set.add((date_obj.strftime('%B'), date_obj.year))
        else:
            # Fallback: best-effort month name, current year
            match = re.search(r'(\w+),\s+(\w+)\s+\d+', date_str)
            if match:
                month_set.add((match.group(2), datetime.now().year))
    
    # Sort months chronologically
    month_order = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    
    sorted_months = sorted(
        month_set,
        key=lambda m: (m[1], month_order.get(m[0], 13))
    )

    if dropped:
        print(f"🧹 Filtered out {dropped} past screenings (before {today.isoformat()})")

    return dict(date_map), sorted_months


def get_theater_class(source: str) -> str:
    """Get CSS class name for a theater based on its source name."""
    for theater_id, info in THEATERS.items():
        if info["name"] == source:
            return theater_id
    return "unknown"


def generate_html(date_map: Dict, sorted_months: List[Tuple]) -> str:
    """
    Generate the complete HTML calendar.
    
    Args:
        date_map: Dictionary mapping dates to lists of films
        sorted_months: List of (month_name, year) tuples
        
    Returns:
        Complete HTML string
    """
    # Calculate stats
    total_screenings = sum(len(films) for films in date_map.values())
    total_days = len(date_map)
    
    html_parts = []
    
    # HTML Header
    html_parts.append("""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Toronto Rep Cinema Calendar</title>
<style>
body { 
    font-family: system-ui, -apple-system, sans-serif; 
    padding: 1rem; 
    margin: 0; 
    background: #f9f9f9; 
    color: #000; 
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
.stats {
    text-align: center;
    margin-bottom: 1rem;
    color: #666;
    font-size: 0.9rem;
}
.filters { 
    display: flex; 
    flex-direction: column; 
    align-items: center; 
    gap: 0.5rem; 
    margin-bottom: 1.5rem; 
}
.filters label {
    font-weight: bold;
    font-size: 0.95rem;
}
.toggle-filters { 
    display: flex; 
    flex-wrap: wrap; 
    gap: 0.5rem; 
    justify-content: center;
}
.toggle { 
    padding: 0.4rem 1rem; 
    font-size: 0.9rem; 
    border-radius: 10px; 
    border: none; 
    color: white; 
    cursor: pointer; 
    font-weight: bold;
    transition: opacity 0.2s;
}
.toggle:hover { opacity: 0.9; }
.toggle.inactive { opacity: 0.4; }
""")
    
    # Theater-specific styles
    for theater_id, info in THEATERS.items():
        color = info["color"]
        html_parts.append(f"""
.toggle.{theater_id} {{ background-color: {color}; }}
.{theater_id} .time {{ background-color: {color}; }}
""")
    
    html_parts.append(""".view-buttons { 
    margin-bottom: 1rem; 
    text-align: center;
}
.view-buttons button { 
    padding: 0.4rem 1rem; 
    font-size: 1rem; 
    margin: 0 0.3rem; 
    cursor: pointer;
    border: 1px solid #ccc;
    background: white;
    border-radius: 5px;
}
.view-buttons button:hover { background: #f0f0f0; }
.hidden { display: none; }
.grid { 
    display: grid; 
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); 
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
    display: flex; 
    align-items: center; 
    gap: 0.5rem; 
}
.time { 
    padding: 0.2rem 0.5rem; 
    border-radius: 5px; 
    font-size: 0.75rem; 
    font-weight: bold; 
    color: white; 
    white-space: nowrap;
    min-width: 65px;
    text-align: center;
}
.film a { 
    text-decoration: none; 
    color: #333; 
    flex: 1;
}
.film a:hover { 
    text-decoration: underline; 
    color: #000;
}
@media (max-width: 768px) {
    body { padding: 0.5rem; }
    h1 { font-size: 1.2rem; }
    .grid { grid-template-columns: 1fr; }
    .toggle { padding: 0.3rem 0.6rem; font-size: 0.8rem; }
}
</style>
</head>
<body>
<h1>🎬 Toronto Rep Cinema Calendar</h1>
<div class='stats'>
    {total_screenings} screenings across {total_days} days
</div>
<div class='filters'>
  <label>🎭 Filter by Theater:</label>
  <div class='toggle-filters'>
""")
    
    # Theater filter buttons
    for theater_id, info in THEATERS.items():
        html_parts.append(
            f"    <button class='toggle {theater_id} active' "
            f"data-source='{info['name']}'>{info['name'].split()[0].upper()}</button>\n"
        )
    
    html_parts.append("""  </div>
  <div class='view-buttons'>
    <button onclick="toggleView('grid-view')">🗓️ Grid View</button>
    <button onclick="toggleView('list-view')">📃 List View</button>
  </div>
</div>
""")
    
    # Grid View
    html_parts.append("<div id='grid-view'>\n")
    
    for month_name, year in sorted_months:
        html_parts.append(f"<h2>{month_name} {year}</h2><div class='grid'>\n")
        
        # Get all dates for this month and sort them
        month_dates = [
            date for date in date_map.keys()
            if month_name in date
        ]
        
        # Sort dates chronologically
        def date_sort_key(date_str):
            match = re.search(r'(\w+),\s+(\w+)\s+(\d+)', date_str)
            if match:
                day_num = int(match.group(3))
                return day_num
            return 0
        
        month_dates.sort(key=date_sort_key)
        
        for date in month_dates:
            films = date_map[date]
            html_parts.append(f"<div class='day-box'><h3>{date}</h3>\n")
            
            for film in films:
                theater_class = get_theater_class(film['source'])
                time_str = extract_time(film['showtime'])
                
                html_parts.append(
                    f"<div class='film {theater_class}' data-source='{film['source']}'>"
                    f"<span class='time'>{time_str}</span>"
                    f"<a href='{film['link']}' target='_blank' title='{film['source']}'>{film['title']}</a>"
                    f"</div>\n"
                )
            
            html_parts.append("</div>\n")
        
        html_parts.append("</div>\n")
    
    html_parts.append("</div>\n")
    
    # List View
    html_parts.append("<div id='list-view' class='hidden'>\n")
    
    for month_name, year in sorted_months:
        html_parts.append(f"<h2>{month_name} {year}</h2>\n")
        
        month_dates = [
            date for date in date_map.keys()
            if month_name in date
        ]
        month_dates.sort(key=date_sort_key)
        
        for date in month_dates:
            films = date_map[date]
            html_parts.append(f"<div class='list-day'><h2>{date}</h2>\n")
            
            for film in films:
                theater_class = get_theater_class(film['source'])
                time_str = extract_time(film['showtime'])
                
                html_parts.append(
                    f"<div class='film {theater_class}' data-source='{film['source']}'>"
                    f"<span class='time'>{time_str}</span>"
                    f"<a href='{film['link']}' target='_blank' title='{film['source']}'>{film['title']}</a>"
                    f"</div>\n"
                )
            
            html_parts.append("</div>\n")
        
    html_parts.append("</div>\n")
    
    # JavaScript
    theater_names = '", "'.join([info['name'] for info in THEATERS.values()])
    
    html_parts.append(f"""<script>
const activeSources = new Set(["{theater_names}"]);

function updateFilters() {{
  document.querySelectorAll('.film').forEach(film => {{
    const source = film.getAttribute('data-source');
    film.style.display = activeSources.has(source) ? 'flex' : 'none';
  }});
  
  document.querySelectorAll('.day-box, .list-day').forEach(day => {{
    const visible = Array.from(day.querySelectorAll('.film'))
      .some(film => film.style.display !== 'none');
    day.style.display = visible ? 'block' : 'none';
  }});
}}

function toggleFilter(button) {{
  const source = button.getAttribute('data-source');
  
  if (activeSources.has(source)) {{
    activeSources.delete(source);
    button.classList.remove('active');
    button.classList.add('inactive');
  }} else {{
    activeSources.add(source);
    button.classList.add('active');
    button.classList.remove('inactive');
  }}
  
  updateFilters();
}}

function toggleView(viewId) {{
  document.getElementById('grid-view').classList.add('hidden');
  document.getElementById('list-view').classList.add('hidden');
  document.getElementById(viewId).classList.remove('hidden');
}}

window.onload = function() {{
  document.querySelectorAll('.toggle').forEach(btn => {{
    btn.addEventListener('click', () => toggleFilter(btn));
  }});
  
  toggleView('grid-view');
  updateFilters();
}}
</script>
</body>
</html>""")
    
    return "\n".join(html_parts)


def main():
    """Main entry point for calendar generation."""
    print("📅 Generating Toronto Rep Cinema Calendar...")
    
    # Load all film data
    all_films = load_all_films()
    print(f"📊 Total films loaded: {len(all_films)}")
    
    if not all_films:
        print("❌ No films to display!")
        return
        
    # Parse and organize (with time sorting!)
    date_map, sorted_months = parse_and_organize_films(all_films)
    print(f"📆 Organized into {len(date_map)} days across {len(sorted_months)} months")
    print(f"✅ Films sorted chronologically within each day")
    
    # Generate HTML
    html = generate_html(date_map, sorted_months)
    
    # Save output
    with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"✅ Calendar saved to {HTML_OUTPUT}")
    
    # Print summary
    total_screenings = sum(len(films) for films in date_map.values())
    print(f"\n📊 Summary:")
    print(f"   • {total_screenings} total screenings")
    print(f"   • {len(date_map)} days with screenings")
    print(f"   • {len(sorted_months)} months covered")


if __name__ == "__main__":
    main()
