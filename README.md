# Smallholder Dry Season Irrigation Dataset

## Overview
This repository defines and executes the sampling protocol for the smallholder dry season irrigation dataset in arid/semi-arid regions of Sub-Saharan Africa with a single rainy season. The goal is to ensure consistent, reproducible, and well-documented sampling that aligns with data download, labeling processes, and final dataset creation.

## Workflow
Generating this dataset requires four main steps. First, the area of interest and places to be sampled must be defined. Second, these regions are manually labeled for smallholder dry season irrigation presence using Earth Collect and Google Earth Pro, using any high reslution dry season imagery avaialable at that location. Third, satellite data is downloaded from Google Earth Engine and aligned with the sampling locations. Finally, the data is processed and cleaned to create the final dataset.

1. **Sampling:**
   - Generate AOIs and sampling grids automatically.
   - Export to Collect surveys for manual annotation.

2. **Labeling:**
   - Use Collect survey tools to generate field labels.
   - Store labels with associated metadata.

3. **Feature Extraction:**
   - Download publicly available satellite data from Google Earth Engine.
   - Ensure alignment with sampling locations and configurations.

4. **Data Processing:**
   - Clean and integrate labels with satellite features.
   - Prepare final datasets for analysis or model training.

## Repository Structure
```
smallholder-irrigation-dataset/
├── data/
│   ├── sampling/              # AOI files, sampling grids, locations, and metadata
│   ├── labels/                # Collect survey files and generated labels with metadata
│   ├── features/              # Data downloaded from Google Earth Engine linked to sampling locations
│   └── final_dataset/         # The cleaned, standardized dataset ready for analysis or publication
├── src/
│   ├── sampling/              # Source code for AOI generation, grid creation, and sampling workflows
│   ├── labels/                # Source code for Collect survey creation and label management
│   ├── features/              # Source code for automated GEE data downloads
│   └── processing/            # Source code for data cleaning, processing, and integration
├── utils/                     # Utility scripts for tasks like metadata generation
├── scripts/
│   ├── sampling/              # Scripts to execute sampling workflows
│   ├── labels/                # Scripts to manage Collect surveys
│   ├── features/              # Scripts for automated data downloads
│   └── processing/            # Scripts for data cleaning and integration
├── notebooks/                 # Jupyter notebooks for exploration, prototyping, and documentation
├── config.yaml                # Central configuration file (paths, EPSG codes, bounding box sizes)
├── README.md                  # Project overview, instructions, and workflow descriptions
├── CONTRIBUTING.md            # Guidelines for contributing to the repository
├── requirements.txt           # Python dependencies
└── tests/                     # Unit tests for critical functions
```

## Getting Started

### Prerequisites
- Python 3.8 or later
- Google Earth Engine API access
- Collect survey tools (e.g., ODK Collect)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/smallholder-irrigation-dataset.git
   cd smallholder-irrigation-dataset
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Configure settings in `config.yaml`.

## Configuration
All project paths, sampling parameters, and GEE download settings are specified in `config.yaml` for easy management.

## Contribution Guidelines
If you wish to contribute, please review `CONTRIBUTING.md` for details on our code of conduct, submission process, coding standards, and coding guidelines.
