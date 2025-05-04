# Cartography State File and Drift Detection CLI

A Python CLI application for managing cartography state files and detecting infrastructure drift.

## Description

This tool provides two main modules:

1. **Get_State**: Manages cartography state files by checking for specific folder structure, handling timestamp-based JSON files, and executing cartography commands.

2. **Get_Drift**: Detects infrastructure drift by analyzing cartography state files, managing drift files in an archive structure, and collecting drift data into a consolidated JSON object.

## Installation

Clone the repository and install the package:

```bash
git clone <repository-url>
cd <repository-directory>
pip install -e .
```

## Usage

The CLI provides two main commands:

### Get State

Retrieve cartography state files:

```bash
python main.py get-state --path /path/to/base/directory --verbose
```

### Get Drift

Detect infrastructure drift and generate consolidated drift data:

```bash
python main.py get-drift --path /path/to/base/directory --output drift_report.json
```

### Options

- `--path`: Path to the parent directory containing the 'drift-detect' folder (required)
- `--output`: (Only for get-drift) Output file path to save consolidated drift data in JSON format
- `--verbose`, `-v`: Enable verbose logging

## Expected Directory Structure

For get-state:
```
/path/to/base/directory/
└── drift-detect-archive/
    ├── [timestamp1].json (timestamp files in main folder)
    ├── [timestamp2].json
    ├── state-archive/
    │   └── [old_timestamp_files].json
    ├── subfolder1/
    │   └── (processed by cartography get-state)
    └── subfolder2/
        └── ...
```

For get-drift:
```
/path/to/base/directory/
└── drift-detect/
    ├── subfolder1/
    │   ├── [timestamp1].json
    │   ├── [timestamp2].json
    │   ├── drift_[identifier].json
    │   └── drift_archive/
    │       └── [old_drift_files].json
    └── subfolder2/
        ├── ...
```

