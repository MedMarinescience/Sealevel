@echo off
cd /d "%~dp0"
echo TUDES Sea Level Scraper - Main Menu
echo.
python main_programme_TUDES_scrapper_sea_level.py
if errorlevel 1 (
  echo.
  echo If Python was not found, install Python 3.10+ and run: pip install -r requirements.txt
  pause
)
