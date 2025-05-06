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
.
├── config.yaml                # Project configuration file
├── CONTRIBUTING.md            # Contribution guidelines
├── LICENSE                    # License file
├── README.md                  # (Superseded by this version)
├── requirements.txt           # Python dependencies
├── notebooks/                 # Jupyter notebooks for data exploration and prototyping
├── src/                       # Main source code folder
│   ├── processing/            # Scripts to clean, merge, and convert survey and polygon data
│   ├── sampling/              # Grid-based sampling code
│   ├── labels/                # Label generation and formatting utilities
│   ├── features/              # Placeholder for feature extraction scripts
│   └── utils/                 # Shared utility functions (e.g., figures, geometries)
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
   python -m venv irr-venv
   source irr-venv/bin/activate
   pip install -r requirements.txt
   ```

   Alternatively, you can use `conda` to create a new environment and install the dependencies:
   ```bash
   conda create --name smh_irr_labels python=3.12
   conda activate smh_irr_labels
   pip install -r requirements.txt
   ```
3. Configure settings in `config.yaml`.

## Configuration
All project paths, sampling parameters, and GEE download settings are specified in `config.yaml` for easy management. 

### Data paths
Data is assumed to be stored locally, under data/ in the root repository. However, if it is stored elsewhere, this path can be specified as server_data_root in the configuration file, and if this directory can be found the data location will be updated accordingly (see utils).

## Contribution Guidelines
If you wish to contribute, please review `CONTRIBUTING.md` for details on our code of conduct, submission process, coding standards, and coding guidelines.
