#!/bin/bash
# =========================================
# Toronto Rep Cinema Calendar - Auto Deploy
# =========================================

echo ""
echo "========================================"
echo "TORONTO REP CINEMA CALENDAR"
echo "Auto-Update and Deploy to GitHub"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3 first."
    exit 1
fi

echo "Starting automated deployment..."
echo ""

# Run the deployment script
python3 deploy.py

# Check if deployment was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "SUCCESS! Calendar deployed to GitHub"
    echo "========================================"
    echo ""
    echo "Your calendar should be live in 2-3 minutes at:"
    echo "https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/"
    echo ""
else
    echo ""
    echo "========================================"
    echo "DEPLOYMENT FAILED"
    echo "========================================"
    echo ""
    echo "Please check the error messages above."
    echo ""
    exit 1
fi
