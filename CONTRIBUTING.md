# Contributing to the Smallholder Dry Season Irrigation Dataset

Thank you for your interest in contributing to this project! This document outlines the key guidelines for managing data and metadata to ensure consistency and reproducibility.

## Data and Metadata Storage Guidelines

### **1. Data Storage:**
- **Directory Structure:**
  - Store data in relevant folders under `data/` (e.g., `data/sampling/`, `data/labels/`, `data/features/`).
  - Use descriptive file names that clearly indicate the content and version if applicable.

- **File Formats:**
  - Preferred formats include CSV, JSON, YAML, and Pickle depending on the data type.
  - For tabular data, use CSV or Parquet.
  - For hierarchical or configuration data, use JSON or YAML.

### **2. Metadata Requirements:**
- Every data file must have an associated metadata file stored in the same directory.
- Metadata should be saved in JSON format with the same base name as the data file, followed by `_metadata.json`.
  - Example:
    ```
    data/features/satellite_data.csv
    data/features/satellite_data_metadata.json
    ```

- **Required Metadata Fields:**
  - `created_at`: Timestamp when the data was generated (ISO 8601 format).
  - `source`: Name of the data file.
  - `description`: Brief description of the dataset.
  - `file_format`: Format of the data file.
  - `created_by`: Relative path of the script that generated the data.

### **3. Data Saving Protocol:**
- Use the `save_data()` utility function to ensure data and metadata are saved consistently.
- When adding new data processing scripts:
  - Ensure they include metadata generation.
  - Store raw and processed data in separate directories if applicable.

### **4. Configuration Management:**
- All paths and environment-specific variables should be stored in `config.yaml`.
- Avoid hardcoding file paths within scripts; use helper functions like `get_data_root()`.

## General Contribution Notes
- Keep code modular and well-documented.
- Follow existing coding patterns and naming conventions.
- Test your code before submitting changes.

Thank you for maintaining the quality and consistency of this project!
