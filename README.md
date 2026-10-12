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

**Storage Analysis (`storage_analysis.py`)**

* ✓ Category distribution with file counts, total size, and percentage breakdown
* ✓ Top-N largest files ranking across full directory trees
* ✓ Top-N largest subdirectories ranking by recursive size
* ✓ Formatted CLI preview tables with aligned sizes and totals

**File Inspector (`file_inspector.py`)**

* ✓ Deep filesystem metadata inspection for both files and directories
* ✓ Detects file category, raw and formatted size, extension, and MIME type
* ✓ Unix file permissions in octal notation (`0o644`, `0o755`)
* ✓ Creation and modification timestamps with cross-platform support
* ✓ Clean key-value metadata preview card

**File Cleanup Tools (`cleanup.py`)**

* ✓ Empty directory preview and safe deepest-first deletion
* ✓ Old file detection and numbered preview
* ✓ Selective file deletion by index with user confirmation
* ✓ Duplicate file cleanup engine with customizable original selection strategies (oldest, newest, shortest path)
* ✓ Duplicate cleanup plan generation and formatted terminal preview
* ✓ Safe duplicate removal preserving original copies with full operation logging
* ✓ Full operation logging to `operations.jsonl` for every deleted file and directory

**Batch File Renamer (`batch_renamer.py`)**

* ✓ Multi-rule name generation engine (prefix, suffix, find-and-replace, custom base name)
* ✓ Sequential number indexing with configurable start number and zero-padding (`_001`, `_002`)
* ✓ Letter case transformations (lowercase, uppercase, title case) and extension remapping
* ✓ Extension-based filtering (`filter_ext`) for targeted batch processing
* ✓ Proactive collision detection checking against existing disk files and intra-batch name conflicts
* ✓ Non-destructive dry-run rename plan creation and aligned terminal preview table
* ✓ Atomic per-file execution with individual failure isolation
* ✓ Full integration with operation logger (`operations.jsonl`) enabling 100% undo via `undo.py`

**Web Application & REST API (`app/routes.py`, `fastapi_app.py`, `run.py`)**

* ✓ Dual Backend Architecture: Fully ported across both **Flask** and **FastAPI**
* ✓ Automatic Swagger / OpenAPI interactive documentation UI at `/docs` (FastAPI)
* ✓ Pydantic request body validation and schemas (`CleanupRequest`, `RenameRequest`)
* ✓ 12 REST API Endpoints implemented and tested:
  * `GET /api/inspect?path=...` — Metadata, permissions, MIME type, and category inspection
  * `GET /api/storage?path=...` — Category distribution, total file counts, and storage metrics
  * `GET /api/duplicates?path=...` — 3-pass hash-grouped duplicate detection clusters
  * `POST /api/duplicates/cleanup?path=...&strategy=...` — Automated duplicate deletion preserving 1 original
  * `POST /api/rename/preview` — Dry-run preview of batch renames and collision detection
  * `POST /api/rename/execute` — Execute batch renaming with rollback logging
  * `GET /api/organise/create?path=...` — Dry-run preview of organization moves
  * `POST /api/organise/execute?path=...` — Safe plan execution with collision handling
  * `GET /api/logs?limit=...` — Reverse-chronological structured operation log history
  * `POST /api/undo` — Ground-truth atomic rollback for move and rename operations
  * `GET /api/cleanup/preview?path=...&days=...` — Preview empty directories and stale files
  * `POST /api/cleanup/delete` — Selective or automated deletion of empty folders and old files

### To Add

* ✗ Custom Web Dashboard Frontend UI (Stage 6)
* ✗ Automated test suite (`unittest` / `pytest`)

## Running the Application

### 1. FastAPI (Recommended — Interactive Docs)

Start the FastAPI server with live reload:

```bash
uvicorn fastapi_app:app --reload
```

* **API Base:** `http://127.0.0.1:8000`
* **Interactive Swagger UI:** `http://127.0.0.1:8000/docs`
* **Redoc Alternative:** `http://127.0.0.1:8000/redoc`

### 2. Flask

Start the Flask development server:

```bash
python run.py
```

* **API Base:** `http://127.0.0.1:5000`

## Project Structure

```text
Personal-Automation-Dashboard/
├── app/
│   ├── __init__.py
│   ├── routes.py            # Flask API blueprint (12 endpoints)
│   ├── automations/
│   │   ├── archiver.py
│   │   ├── batch_renamer.py
│   │   ├── cleanup.py
│   │   ├── directory_cache.py
│   │   ├── duplicate_finder.py
│   │   ├── file_categories.py
│   │   ├── file_inspector.py
│   │   ├── file_tools.py
│   │   ├── logger.py
│   │   ├── storage_analysis.py
│   │   └── undo.py
│   └── logs/
│       └── operations.jsonl
├── fastapi_app.py           # FastAPI application & Pydantic models (12 endpoints)
├── run.py                   # Flask runner
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
