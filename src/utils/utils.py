import os
import yaml
import json
import pandas as pd
import pickle
from datetime import datetime

# Helper function to find the project root
def find_project_root(current_path):
    """
    Recursively find the project root by locating the config.yaml file
    and ensuring the directory is named 'smallholder-irrigation-dataset'.

    Parameters:
        current_path (str): The starting path to search upwards from.

    Returns:
        str: The absolute path to the project root directory.
    """
    while current_path != os.path.dirname(current_path):
        if ("config.yaml" in os.listdir(current_path) and 
            os.path.basename(current_path) == "smallholder-irrigation-dataset"):
            return current_path
        current_path = os.path.dirname(current_path)
    raise FileNotFoundError("Could not find 'smallholder-irrigation-dataset' directory with config.yaml in any parent directory.")

# Load configuration
def load_config():
    """
    Load project configuration from the project root directory.

    Returns:
        dict: Configuration settings.
    """
    current_dir = os.getcwd()
    project_root = find_project_root(current_dir)
    config_path = os.path.join(project_root, "config.yaml")

    with open(config_path, "r") as file:
        return yaml.safe_load(file)

# Determine the root data directory
def get_data_root():
    """
    Determine whether the code is running locally or on a server
    and return the appropriate data root directory.

    Returns:
        str: Path to the data root directory.
    """
    config = load_config()
    local_root = os.path.join(find_project_root(os.getcwd()), 'data')
    server_root = config.get('server_data_root', '/home/waves/data/smallholder-irrigation-dataset/data/')

    # Check for server environment
    if os.path.exists(server_root):
        return server_root
    else:
        return local_root

# Save data with metadata
def save_data(data, output_path, description=None, file_format='csv'):
    """
    Save data to the specified output path in a flexible format, creating directories as needed,
    and optionally save metadata.

    Parameters:
        data (any): Data to be saved (supports JSON, CSV, Pickle, YAML).
        output_path (str): Path where the data should be saved.
        description (str, optional): Description of the data.
        file_format (str, optional): Format to save the data (json, csv, pickle, yaml). Inferred from file extension if not provided.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Infer file format from extension if not provided
    if not file_format:
        file_format = output_path.split('.')[-1].lower()

    # Save data based on the format
    if file_format == 'json':
        with open(output_path, "w") as f:
            json.dump(data, f)
    elif file_format == 'csv':
        if isinstance(data, pd.DataFrame):
            data.to_csv(output_path, index=False)
        else:
            raise ValueError("Data must be a pandas DataFrame to save as CSV.")
    elif file_format == 'pickle':
        with open(output_path, "wb") as f:
            pickle.dump(data, f)
    elif file_format == 'yaml':
        with open(output_path, "w") as f:
            yaml.dump(data, f)
    else:
        raise ValueError(f"Unsupported file format: {file_format}")

    # Automatically generate metadata
    metadata = {
        "created_at": datetime.now().isoformat(),
        "source": os.path.basename(output_path),
        "description": description,
        "file_format": file_format,
        "created_by": os.path.relpath(__file__, start=find_project_root(os.getcwd()))  # Captures the file that created the data
    }

    # Save metadata alongside the data file
    metadata_path = output_path.rsplit('.', 1)[0] + "_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f)
