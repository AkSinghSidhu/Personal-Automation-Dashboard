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
* ✓ SHA-256 file hashing
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

**File Organizer (`file_categories.py`)**
* ✓ 18-category file classification system (Images, Videos, Audio, Documents, Code, etc.)
* ✓ File category detection by extension
* ✓ Destination path calculation
* ✓ Organization plan generation (non-destructive planning phase)
* ✓ Safe organization execution with full collision handling:
  * ✓ Destination existence check
  * ✓ File size comparison
  * ✓ Hash-based duplicate detection
  * ✓ Automatic filename collision resolution (`photo_1.jpg`, `photo_2.jpg`, ...)
  * ✓ True duplicate skipping (same hash → file not moved)

**Duplicate Finder (`duplicate_finder.py`)**
* ✓ Recursive duplicate file scanning
* ✓ Size-first grouping (eliminates unique files without hashing)
* ✓ Hash-based confirmation of true duplicates
* ✓ Confirmed duplicate groups returned for review

### To Add

* ✗ Error handling for file operations
* ✗ Operation logging
* ✗ Undo / rollback
* ✗ Duplicate file management (delete / retain selected)
* ✗ Storage analysis (type distribution, usage breakdown)
* ✗ Cleanup tools (temp files, empty directories)
* ✗ Batch rename, archive tools
* ✗ Automated test suite
* ✗ User-friendly web interface

## Project Structure

```text
Personal-Automation-Dashboard/
├── app/
│   └── automations/
│       ├── file_tools.py
│       ├── file_categories.py
│       └── duplicate_finder.py
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