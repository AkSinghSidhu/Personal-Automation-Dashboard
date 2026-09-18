# Personal Automation Dashboard

A Python-based collection of useful automation tools for everyday file and system management.

## Features

### Added

**File Tools (`file_tools.py`)**
* ✓ Folder and file size calculator
* ✓ Human-readable size formatting (B → KB → MB → GB → TB → PB+)
* ✓ Recursive folder and file counter
* ✓ Directory statistics — file count, folder count, total size in a single traversal
* ✓ Contents sorted by size (ascending or descending)
* ✓ Recursive directory size tree — nested structure with sizes bubbling up from children
* ✓ SHA-256 full and partial file hashing
* ✓ Empty directory detection
* ✓ File and folder search with optional type filter (files only / folders only)
* ✓ Filter files by extension (auto-handles `.jpg` or `jpg` input)
* ✓ Recently modified files (within N days)
* ✓ Recently created files (within N days, cross-platform)
* ✓ Old files — files not modified in the last N days
* ✓ Large files — files above a given size threshold
* ✓ File modification time and creation time as standalone utilities
* ✓ File info — name, size, extension, creation time, modification time in one call
* ✓ Sort results by modified time, created time (ascending or descending)
* ✓ Safe file moving (`move_file`) with automatic destination folder creation
* ✓ Safe file renaming (`rename_file`) preserving parent directory

**File Organizer (`file_categories.py`)**
* ✓ 18-category file classification system (Images, Videos, Audio, Documents, Code, etc.)
* ✓ File category detection by extension
* ✓ Destination path calculation
* ✓ Organization plan generation (non-destructive planning phase)
* ✓ Dry-run plan preview mode with summary of planned moves vs skipped files
* ✓ User confirmation prompt before making any filesystem modifications
* ✓ Safe organization execution with full collision handling:
  * ✓ Destination existence check
  * ✓ File size comparison
  * ✓ Hash-based duplicate detection
  * ✓ Automatic filename collision resolution (`photo_1.jpg`, `photo_2.jpg`, ...)
  * ✓ True duplicate skipping (same hash → file not moved)
* ✓ Comprehensive error handling (permission errors, missing files, disk errors)

**Duplicate Finder (`duplicate_finder.py`)**
* ✓ High-performance 3-pass duplicate scanning (File Size → Partial Hash → Full Hash)
* ✓ Size-first grouping (eliminates unique files without hashing)
* ✓ Partial hashing (64 KB chunk check to filter out non-matching candidates quickly)
* ✓ Full SHA-256 confirmation of true duplicates
* ✓ Formatted duplicate groups report with per-group sizes and file lists
* ✓ Total reclaimable / wasted storage calculation

**Operation Logger (`logger.py`)**
* ✓ Structured JSON-Lines operation logging to `app/logs/operations.jsonl`
* ✓ Logs operation type (`move`, `rename_and_move`, `skip_duplicate`, `undo`), timestamp, paths, status, and error messages
* ✓ Log reader utility (`read_logs`) returning structured log records safely
* ✓ Quick retrieval of the most recent operation (`read_last_change`)

**Undo & Rollback Engine (`undo.py`)**
* ✓ Reverses moves and auto-renamed moves using the operation log as ground truth
* ✓ Restores files from `new_path` back to `original_path`
* ✓ Restores original filenames for collision-renamed files in a single step
* ✓ Pre-flight existence checks and safety guards against collisions during undo
* ✓ Dedicated undo logging for tracking rollback history

**Zip Archiver (`archiver.py`)**
* ✓ File list validation filtering out non-existent or inaccessible files
* ✓ Zip archive compression with `ZIP_DEFLATED`
* ✓ Clean archive root structure using relative archive names (`arcname`)
* ✓ Configurable output path with automatic parent directory creation

**Directory Size Caching (`directory_cache.py`)**
* ✓ SQLite + SQLAlchemy database caching for directory tree sizes
* ✓ Fast query layer for instant macroscopic folder size lookups

### To Add

* ✗ Duplicate file deletion / cleanup action (delete duplicates, keep original)
* ✗ Storage analysis dashboard (category distribution, largest files breakdown)
* ✗ File cleanup tools (automated temporary file scanner, empty directory cleaner)
* ✗ Batch file renamer (prefix, suffix, sequential numbering, find-and-replace)
* ✗ Automated test suite (`unittest` / `pytest`)
* ✗ GUI / Web interface (Stage 6)

## Project Structure

```text
Personal-Automation-Dashboard/
├── app/
│   ├── automations/
│   │   ├── archiver.py
│   │   ├── directory_cache.py
│   │   ├── duplicate_finder.py
│   │   ├── file_categories.py
│   │   ├── file_tools.py
│   │   ├── logger.py
│   │   └── undo.py
│   └── logs/
│       └── operations.jsonl
└── README.md
```

## Goal

Build a collection of practical automation tools while improving my skills in:

* Python
* File and directory handling
* Object-oriented and modular programming
* Error handling
* Testing
* Working with databases
* Flask
* FastAPI
* SQL and SQLite
* Building practical backend applications

The goal is to turn the project into a useful automation dashboard while learning and applying these concepts through real features.