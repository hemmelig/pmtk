# Project Management Toolkit (pmtk)
*A lightweight, opinionated project structure and management tool for my research projects.*

`pmtk` initialises, organises, and manages research projects in a consistent and reproducible way. It standardises directory layout, handles virtual environments, tracks datasets and documents, and provides simple automation commands for project metadata, archiving, and provenance.

I am using this to improve the reliability and reproducibility of my projects, and to ensure a clear separation between raw data, processed data, analysis, and outputs.

---

## Features

- Initialise new projects with a clean, well-structured directory layout
- Manage Python/conda environments in a reproducible way
- Register datasets and do basic tracking of ownership, modification, etc.
- Maintain a structured record of project metadata, status, and contacts
- Provide clean separation between active work, final results, and archived materials
- Lightweight command-line interface (`pmtk <command>`)

---

## Default Project Structure

```
<project_name>/
├── archive/
├── config/
│   ├── contacts.yaml
│   ├── data_registry.yaml
│   ├── environment.yaml
│   ├── project.yaml
│   └── registry.yaml
│   ├── tasks.yaml
├── data/
│   ├── external/
│   ├── internal/
│   ├── metadata/
│   └── processed/
├── docs/
│   ├── budget/
│   ├── proposal-and-contract/
│   ├── publications-and-outreach/
│   ├── risks/
│   ├── status/
│   └── workplan/
├── environments/
│   ├── .venv1/
│   ├── .venv2/
│   ├── .../
├── logs/
│   └── pipeline/
│   ├── pmtk/
├── maps/
├── notes/
│   └── YYYY-MM-DD.md
├── reports/
│   ├── drafts/
│   ├── final/
├── results/
│   ├── figures/
│   ├── tables/
│   ├── models/
├── tests/
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
Raw data is immutable in `data/`, processed data is separate, and environments are tracked in `environments/`.

### **2. Discoverable Documentation**
All project documentation lives under `docs/`.

### **3. Work Unit Separation**
`workspace/` for active work, `results/` for outputs, `archive/` for retired/completed components.

### **4. Extensible Configuration**
All metadata lives in modular YAML files under `config/`.

---

## Usage Overview

Some of the basic commands are shown below:

```bash
pmtk init <project_name> [--git]
pmtk data register <path>
pmtk work_unit add <unit-name>
pmtk work_unit archive <unit-name>
pmtk status
pmtk tag <project-tag>
```

---

## Roadmap

- Remote syncing
