# AGENTS.md

## Cursor Cloud specific instructions

### Overview

TUDES Sea Level Data Scraper — a collection of Python scripts that download oceanographic data from the Turkish National Sea Level Monitoring System (TUDES) at `https://tudes.harita.gov.tr`. See `README.md` for full project description and file listing.

### Running the application

- Entry point: `python3 main_programme_TUDES_scrapper_sea_level.py` (interactive CLI menu with `input()` prompts)
- All scripts are interactive and require stdin input; pipe choices when automating (e.g. `echo "7" | python3 main_programme_TUDES_scrapper_sea_level.py`)

### Key caveats

- **External API dependency**: All scrapers make live HTTPS requests to `tudes.harita.gov.tr`. There are no mocks, stubs, or local test data. The TUDES API may be unreachable from cloud VMs (connection resets observed). This is an environment limitation, not a code bug.
- **No automated test suite**: The only "test" is `test_tudes_connection.py`, which tests live network connectivity. There are no unit tests.
- **No linter config**: The project has no configured linter. Use `pyflakes *.py` for basic static checks. Pre-existing warnings exist (unused imports in `tudes_selenium_scraper.py` and `tudes_robust_scraper.py`).
- **Offline testable component**: `tudes_json_to_excel.py` (and its `convert_json_folder` function) can be tested without network by creating sample JSON files under `tudes_data/`.

### Lint / check

```bash
pyflakes *.py
python3 -m py_compile <script>.py  # syntax check individual files
```

### Testing the JSON-to-Excel converter (offline)

```python
from tudes_json_to_excel import convert_json_folder
convert_json_folder('tudes_data/<subfolder>')
```
