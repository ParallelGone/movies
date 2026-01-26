# Quick GitHub Deployment Setup

## One-Time Setup (Do this first!)

### 1. Initialize Git Repository (if not already done)

```bash
cd /path/to/your/toronto-cinema-project

# Initialize git
git init

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git

# Or if using SSH:
git remote add origin git@github.com:YOUR-USERNAME/YOUR-REPO-NAME.git

# Create initial commit
git add .
git commit -m "Initial commit"

# Push to GitHub
git push -u origin main
```

### 2. Enable GitHub Pages

1. Go to your GitHub repository
2. Click **Settings** → **Pages** (in left sidebar)
3. Under "Source":
   - Branch: **main**
   - Folder: **/ (root)**
4. Click **Save**
5. Your site will be live at: `https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/`

---

## Daily Usage

### Option 1: Full Automated Update (Recommended)

```bash
python deploy.py
```

This will:
- ✅ Run all scrapers
- ✅ Generate the calendar
- ✅ Commit changes
- ✅ Push to GitHub
- ✅ Your site updates automatically!

### Option 2: Manual Control

```bash
# Just scrape (no deploy)
python deploy.py --scrape-only

# Skip scraping, deploy existing data
python deploy.py --skip-scrape

# Commit but don't push (test locally first)
python deploy.py --no-push

# Continue even if some scrapers fail
python deploy.py --continue-on-error
```

---

## Scheduling Automatic Updates

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. **Name:** "Update Cinema Calendar"
4. **Trigger:** Daily at 8:00 AM
5. **Action:** Start a program
   - Program: `python`
   - Arguments: `deploy.py`
   - Start in: `C:\path\to\your\project`

### Mac/Linux Cron

```bash
# Edit crontab
crontab -e

# Run daily at 8 AM
0 8 * * * cd /path/to/project && python3 deploy.py

# Or twice daily (8 AM and 8 PM)
0 8,20 * * * cd /path/to/project && python3 deploy.py
```

---

## Troubleshooting

### "Not in a git repository"
```bash
git init
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
```

### "No git remote configured"
```bash
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
```

### "Permission denied (publickey)"
Use HTTPS instead of SSH:
```bash
git remote set-url origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
```

### "Push rejected, fetch first"
```bash
git pull origin main --rebase
git push origin main
```

### GitHub Pages not updating
1. Wait 2-3 minutes (GitHub Pages takes time to rebuild)
2. Hard refresh browser: `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)
3. Check GitHub Actions tab for build errors

---

## File Structure

Your project should look like this:

```
toronto-cinema-calendar/
├── scrapers/
│   ├── fox.py
│   ├── paradise.py
│   ├── revue.py
│   ├── tiff.py
│   └── kingsway.py
├── data/
│   ├── fox_films.json
│   ├── paradise_films.json
│   └── ... (other JSON files)
├── generator.py          # Calendar generator
├── deploy.py             # ← NEW! Deployment script
├── index.html            # Generated calendar (auto-updated)
├── requirements.txt
└── README.md
```

---

## Quick Commands Reference

```bash
# Full update (most common)
python deploy.py

# Test without pushing
python deploy.py --no-push

# Update with existing data
python deploy.py --skip-scrape

# Check git status
git status

# View commit history
git log --oneline

# Undo last commit (keep changes)
git reset --soft HEAD~1
```

---

## Success!

Once set up, your workflow is simple:

1. Run `python deploy.py`
2. Wait 2-3 minutes
3. Visit `https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/`
4. Your calendar is updated! 🎉

---

## Advanced: GitHub Actions (Fully Automated)

For completely hands-off updates, create `.github/workflows/update.yml`:

```yaml
name: Update Calendar

on:
  schedule:
    - cron: '0 8,20 * * *'  # 8 AM and 8 PM daily
  workflow_dispatch:  # Manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run deployment
        run: python deploy.py --continue-on-error
```

This runs automatically on schedule - no manual intervention needed!
