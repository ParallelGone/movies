import subprocess
print("🧩 Generating updated calendar...")
subprocess.run(["python", "generate_calendar_with_fox_stylefix.py"])

print("✅ Calendar updated and saved to calendar_grid.html")

print("📤 Publishing calendar to GitHub Pages...")

subprocess.run(["git", "add", "index.html"])
subprocess.run(["git", "commit", "-m", "📅 Auto-update calendar"])
subprocess.run(["git", "push"])

print("✅ Published to GitHub.")