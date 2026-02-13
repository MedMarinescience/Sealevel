#!/bin/sh
cd "$(dirname "$0")"
echo "TUDES Sea Level Scraper - Main Menu"
echo ""
python3 main_programme_TUDES_scrapper_sea_level.py 2>/dev/null || python main_programme_TUDES_scrapper_sea_level.py
if [ $? -ne 0 ]; then
  echo ""
  echo "If Python was not found, install Python 3.10+ and run: pip install -r requirements.txt"
  read -r -p "Press Enter to close..."
fi
