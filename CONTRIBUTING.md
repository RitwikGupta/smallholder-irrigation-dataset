# Contributing to the Smallholder Dry Season Irrigation Dataset

Thank you for your interest in contributing to this project! This document outlines the key guidelines for managing data and metadata to ensure consistency and reproducibility.

## General Contribution Notes
- Commit frequently with detailed commit messages and descriptions, especially when actively collaborating with others. 
- Update README.md files obsessively as changes to the repository and sub-repositories happen. 

## Data and Metadata Storage Guidelines

### **1. Data Storage:**
- **Directory Structure:**
  - Store data in relevant folders under `data/` that correspond with the `src` module they were created under(e.g., `data/sampling/`, `data/labels/`, `data/features/`).
  - Use descriptive file names that clearly indicate the content and version if applicable.

### **2. Data Saving Protocol:**
- Use the `save_data()` utility function to ensure data and metadata are saved consistently.

- **Automatically Generated Metadata Fields:**
  - `date`: Timestamp when the data was generated (ISO 8601 format).
  - `file`: Name of the data file.
  - `description`: Brief description of the dataset.
  - `file_format`: Format of the data file.
  - `source`: Relative path of the script that generated the data.

### **3. Configuration Management:**
- Paths and environment-specific variables can be stored in `config.yaml`.
- Never hardcode file paths within scripts; use helper functions like `get_data_root()`.

### **4. Data in the .gitignore:**
- By default, data should be listed in the `.gitignore`. However, if the file is small enough and it is useful to add it to the repository, it can be removed. 

Thank you for maintaining the quality and consistency of this project!
