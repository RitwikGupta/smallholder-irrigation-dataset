import os
from survey_to_csv import process_xml_zip
from polygons_to_geojson import kml_to_geojson
import pandas as pd
from merge_survey_and_polygons import merge_and_check

# process a folder full of completed surveys

def process_and_merge_folder(folder_path):
    """
    Processes and merges all raw survey maching polygon files in a specified folder.
    This function iterates through all files in the given folder, processes
    `.kml` and `.zip` files using specific helper functions, and merges the
    resulting processed `.csv` files into a single DataFrame.
    Args:
        folder_path (str): The path to the folder containing the files to process.
    Returns:
        pandas.DataFrame: A DataFrame containing the merged results of all processed `.csv` files.
    Notes:
        - `.kml` files are converted to GeoJSON using the `kml_to_geojson` function.
        - `.zip` files are processed using the `process_xml_zip` function.
        - The processed files are expected to be stored in a subfolder named "processed".
        - Only `.csv` files in the "processed" folder are merged.
    Raises:
        FileNotFoundError: If the specified folder or required files do not exist.
        ValueError: If there are issues during the merging process.
    """


    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if file_name.endswith('.kml'):
            kml_to_geojson(file_path)
        elif file_name.endswith('.zip'):
            process_xml_zip(file_path)

    # Merge the processed files
    processed_path = folder_path.replace("/raw", "/processed")
    merged_result = [merge_and_check(os.path.join(processed_path, file)) for file in os.listdir(processed_path) if file.endswith('.csv')]
    merged_result = pd.concat(merged_result, ignore_index=True)
    return merged_result

if __name__ == '__main__':

    # Example usage/test code 
    
    # folder_path = "data/labels/labeled_surveys/random_sample/raw"
    # merged_result = process_and_merge_folder(folder_path)
    # print(merged_result.head())

    # CLI argument parsing

    import argparse

    parser = argparse.ArgumentParser(description="Process and merge all survey files in a folder.")
    parser.add_argument("folder_path", type=str, help="Path to the folder containing survey files.")
    args = parser.parse_args()
    folder_path = args.folder_path

    merged_result = process_and_merge_folder(folder_path)

    print(f"Merged result has {len(merged_result)} rows")