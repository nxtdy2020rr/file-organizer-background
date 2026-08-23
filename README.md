# file-organizer-background - Shared Open Source Project - Open-Source Project

A rules-based file organization utility that monitors a source directory (such as a Downloads or Desktop folder) and automatically categorizes, groups, and routes files into specific subdirectories according to regex matching rules.

## Project Features

- **No external dependencies**: Implemented using pure Python standard library modules (`os`, `re`, `shutil`, `time`, `argparse`).
- **Dynamic rule engine**: Compiles and matches file names using case-insensitive regular expressions defined in a simple `rules.json` file.
- **Auto-generated default rules**: Automatically creates a default `rules.json` config if none is provided on startup.
- **Naming collision protection**: Safely increments filenames (e.g. `document.pdf` becomes `document_1.pdf`) to prevent overwriting existing files in destination folders.
- **Two execution modes**: Run as a continuous background daemon polling every few seconds, or execute a one-off immediate directory scan.
- **Operation logger**: Appends a clear execution audit trail of all moved files to a text log file.

## Repository Layout

```text
file-organizer-background/
├── src/
│   └── sorter.py
├── tests/
│   └── test_sorter.py
└── README.md
```

## Build instructions

Ensure Python (version 3.8 or later) is installed. There are no external dependencies.

## Running the Project

### 1. Run the watcher daemon (polls every 2 seconds by default)

```bash
python src/sorter.py /path/to/my/downloads
```

### 2. Run a single scan pass immediately and exit

```bash
python src/sorter.py /path/to/my/downloads --once
```

### 3. Customize rules

Create or edit the `rules.json` file. Rules are evaluated sequentially (first match wins):

```json
[
  {
    "name": "Images",
    "pattern": "\\.(jpe?g|png|gif|svg)$",
    "destination": "organized/images"
  },
  {
    "name": "Source Code",
    "pattern": "\\.(py|js|rs|cpp|html|css)$",
    "destination": "C:\\Developer\\Code"
  }
]
```

- `pattern`: Regular expression to match filenames.
- `destination`: Destination directory. It can be relative (nested under the monitored source folder) or an absolute system path.

### Options

- `--rules <file>`: Custom rules JSON file path (default: `rules.json`).
- `--log <file>`: Custom log text file path (default: `sorting_log.txt`).
- `--interval <seconds>`: Polling sleep delay for daemon mode (default: `2`).

## Running Tests

Run the test suite using Python's built-in `unittest` framework:

```bash
python -m unittest tests/test_sorter.py
```
This tests rule parsing, naming collision increments, and file scan movements inside clean sandboxed test folders.

---
*Released under the MIT License by Sassywow.*
