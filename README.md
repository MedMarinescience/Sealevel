# TUDES Sea Level Data Scraper

Download sea level and other data from the Turkish National Sea Level Monitoring System (TUDES): https://tudes.harita.gov.tr

---

## Download and run (any PC)

1. **Download everything**  
   Download this folder (or clone the repo). Keep all files in one folder.

2. **Install Python**  
   Use Python 3.10 or newer from [python.org](https://www.python.org/downloads/).  
   On install, check **"Add Python to PATH"**.

3. **Install packages**  
   Open a terminal in this folder and run:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the program**  
   ```bash
   python main_programme_TUDES_scrapper_sea_level.py
   ```  
   Or double‑click `run_main.bat` (Windows) or run `./run_main.sh` (macOS/Linux).

5. **Set your user info (optional)**  
   For options 2 and 3 in the menu, set your name/email/institution so TUDES logs them:
   - **Windows (PowerShell):**
     ```powershell
     $env:TUDES_USER_NAME="Your Name"
     $env:TUDES_USER_EMAIL="you@example.com"
     $env:TUDES_USER_INSTITUTION="Your Institution"
     ```
   - **macOS/Linux:**  
     `export TUDES_USER_NAME="Your Name"` (and same for `TUDES_USER_EMAIL`, `TUDES_USER_INSTITUTION`).

That’s all you need to download the repo and run it on any PC.

---

## What’s in this folder

| File | Purpose |
|------|--------|
| `main_programme_TUDES_scrapper_sea_level.py` | **Start here** – menu to run all options |
| `download_erdemli_data.py` | Simple download for Erdemli station |
| `tudes_scraper_v2.py` | All stations, all data types (recommended) |
| `tudes_selenium_scraper.py` | Browser automation (needs Chrome + ChromeDriver) |
| `tudes_robust_scraper.py` | Fallback when SSL issues occur |
| `test_tudes_connection.py` | Test connection to TUDES |
| `tudes_json_to_excel.py` | Merge JSON chunks into one Excel/CSV |
| `requirements.txt` | Python packages – run `pip install -r requirements.txt` |
| `run_main.bat` | Windows: double‑click to run the main menu |
| `run_main.sh` | macOS/Linux: run main menu from terminal |

---

## Requirements

- **Python** 3.10 or newer  
- **Packages:** `requests`, `pandas`, `openpyxl`, `selenium` (see `requirements.txt`)  
- **Chrome + ChromeDriver** only if you use the Selenium option (3) in the menu  

---

## Output

- Data is saved under `tudes_data/` (created automatically).  
- Use menu option **6** to combine JSON files into one Excel/CSV file.

---

## Troubleshooting

- **Connection/SSL errors:** Run **5. Connection Test** from the menu, or use option **4. Robust Scraper**.  
- **“python not found”:** Install Python and add it to PATH, or try `py main_programme_TUDES_scrapper_sea_level.py` (Windows).  
- **Selenium:** Only for option 3; install [ChromeDriver](https://chromedriver.chromium.org/) if you use it.

---

## Licence and attribution

Developed for Aquatic Ecology Lab, METU-IMS.  
Use of TUDES data should follow the terms of the TUDES portal.
