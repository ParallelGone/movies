import subprocess

print("📤 Publishing calendar to GitHub Pages...")

subprocess.run(["git", "add", "calendar_grid.html"])
subprocess.run(["git", "commit", "-m", "📅 Auto-update calendar"])
subprocess.run(["git", "push"])

print("✅ Published to GitHub.")