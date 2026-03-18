# ⚡ AutoPilot — File & Data Automation Toolkit

A Python CLI tool that automates repetitive file operations: organize files into folders, find duplicates, clean CSV/JSON data, and bulk rename files.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![CLI](https://img.shields.io/badge/Interface-CLI-yellow)

## Features

- **File Organizer** — Auto-sort files into categorized folders (Images, Documents, Code, etc.)
- **Duplicate Finder** — Detect and remove duplicate files using MD5 hash comparison
- **Data Cleaner** — Clean CSV/JSON files: remove duplicates, empty rows, strip whitespace
- **Bulk Renamer** — Rename files with custom patterns ({n}, {date}, {original})
- **Dry Run Mode** — Preview all changes before executing
- **Zero Dependencies** — Uses only Python standard library

## Quick Start

```bash
git clone https://github.com/Manuel20452/autopilot.git
cd autopilot

# No dependencies needed! Just run:
python autopilot.py
```

## Usage

### Interactive Mode
```bash
python autopilot.py
# Choose from the menu: organize, duplicates, clean, or rename
```

### Command Line

#### Organize Files
```bash
# Sort files in Downloads into category folders
python autopilot.py organize ~/Downloads

# Preview first (dry run)
python autopilot.py organize ~/Downloads --dry-run
```

**Output:**
```
📁 Organizing: /home/user/Downloads

  photo.jpg → Images/
  report.pdf → Documents/
  script.py → Code/
  song.mp3 → Audio/
  backup.zip → Archives/

[✓] Moved 5/5 files
```

#### Find Duplicates
```bash
# Scan for duplicates
python autopilot.py duplicates ~/Pictures

# Scan and remove duplicates
python autopilot.py duplicates ~/Pictures --remove
```

**Output:**
```
🔍 Scanning for duplicates in: /home/user/Pictures

  Scanned: 234 files
  Duplicates found: 3 groups

  📄 2.4 MB — 2 copies:
     /Pictures/IMG_001.jpg
     /Pictures/backup/IMG_001.jpg

  💾 Space wasted by duplicates: 7.2 MB
```

#### Clean Data Files
```bash
# Clean a CSV file
python autopilot.py clean messy_data.csv

# Clean and save to specific output
python autopilot.py clean data.json --output clean_data.json
```

**Output:**
```
📊 Loaded 1500 records from messy_data.csv
  [✓] Stripped whitespace from all fields
  [✓] Removed 23 duplicate rows (1477 remaining)
  [✓] Removed 8 rows with empty values

  ==================================================
  DATA SUMMARY
  ==================================================
  Rows: 1469
  Columns: 6
  ==================================================

  [✓] Exported to: messy_data_cleaned.csv
```

#### Bulk Rename
```bash
# Rename with sequential numbers
python autopilot.py rename ~/Photos --pattern "vacation_{n}"

# Preview first
python autopilot.py rename ~/Photos --pattern "{date}_{original}" --dry-run
```

**Output:**
```
✏️ Bulk rename in: /home/user/Photos

  IMG_4521.jpg → vacation_001.jpg
  IMG_4522.jpg → vacation_002.jpg
  IMG_4523.jpg → vacation_003.jpg

[✓] Renamed 3/3 files
```

## As a Python Module

```python
from autopilot import FileOrganizer, DuplicateFinder, DataCleaner, BulkRenamer

# Organize files
FileOrganizer("~/Downloads").organize(dry_run=True)

# Find duplicates
dupes = DuplicateFinder("~/Pictures").find_duplicates()

# Clean data with chaining
DataCleaner("data.csv") \
    .strip_whitespace() \
    .remove_duplicates() \
    .remove_empty() \
    .filter_rows("age", lambda x: int(x) >= 18) \
    .summary() \
    .export("clean_data.csv")

# Bulk rename
BulkRenamer("~/Photos").rename(pattern="trip_{n}", dry_run=True)
```

## File Categories

| Category | Extensions |
|----------|-----------|
| Images | .jpg .png .gif .svg .webp .bmp |
| Documents | .pdf .doc .docx .txt .xlsx .csv .pptx |
| Videos | .mp4 .mkv .avi .mov .webm |
| Audio | .mp3 .wav .flac .aac .ogg |
| Code | .py .js .html .css .java .cpp .sh |
| Archives | .zip .rar .7z .tar .gz |
| Other | Everything else |

## Tech Stack

`Python` `argparse` `hashlib` `pathlib` `CSV` `JSON`

## License

MIT — free to use and modify.

## Author

**Manuel** — Python Developer & Automation Specialist
- GitHub: [@Manuel20452](https://github.com/Manuel20452)
