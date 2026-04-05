# Project Management Toolkit (pmtk)
*A lightweight, opinionated project structure and management tool for my research projects.*

`pmtk` initialises, organises, and manages research projects in a consistent and reproducible way. It standardises directory layout, handles virtual environments, tracks datasets and documents, and provides simple automation commands for project metadata, archiving, and provenance.

I am using this to improve the reliability and reproducibility of my projects, and to ensure a clear separation between raw data, processed data, analysis, and outputs.

---

## Features

- Initialise new projects with a clean, well-structured directory layout
- Integrates with `uv` to manage Python environments cleanly
- Register datasets and do basic tracking of ownership, modification, etc.
- Maintain a structured record of project metadata
- Provide clean separation between active work, final results, and archived materials
- Lightweight command-line interface (`pmtk <command>`)

---

## Default Project Structure

```
<project_name>/
├── archive/
├── .config/
│   ├── data_registry.yaml
│   ├── project.yaml
│   └── unit_registry.yaml
├── data/
│   ├── external/
│   ├── internal/
│   ├── metadata/
│   └── processed/
├── docs/
│   ├── budget/
│   ├── notes/
│   │   └── YYYY-MM-DD.md
│   ├── proposal/
│   ├── publications/
│   ├── reports/
│   │   ├── drafts/
│   │   └── final/
│   └── workplan/
├── results/
│   ├── figures/
│   ├── models/
│   └── tables/
├── tools/
├── workspace/
├── README.md
├── .pmtk-lock
├── .pmignore
└── .gitignore
```

---

## Design Principles

### **1. Reproducible**
Raw data is immutable in `data/` and processed data is separate.

### **2. Discoverable Documentation**
All project documentation lives under `docs/`.

### **3. Work Unit Separation**
`workspace/` for active work, `results/` for outputs, `archive/` for retired/completed components.

### **4. Extensible Configuration**
All metadata lives in modular YAML files under `.config/`.

---

## Usage Overview

Some of the basic commands are shown below:

```bash
pmtk init <project_name> [--git]
pmtk data add <path>
pmtk data show <path>
pmtk data fetch <path>
pmtk unit add <unit-name>
pmtk unit archive <unit-name>
pmtk unit restore <unit-name>
pmtk status
pmtk tag <project-tag>
```
