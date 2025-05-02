import os
from survey_to_csv import process_xml_zip
from polygons_to_geojson import kml_to_geojson
import pandas as pd
from merge_survey_and_polygons import merge_and_check

# process a folder full of completed surveys

def process_and_merge_folder(folder_path):

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if file_name.endswith('.kml'):
            kml_to_geojson(file_path)
        elif file_name.endswith('.zip'):
            process_xml_zip(file_path)

    # Merge the processed files
    processed_path = os.path.join(folder_path, "processed")
    merged_result = [merge_and_check(os.path.join(processed_path, file)) for file in os.listdir(processed_path) if file.endswith('.csv')]
    merged_result = pd.concat(merged_result, ignore_index=True)
    return merged_result

if __name__ == '__main__':
    folder_path = "data/labels/labeled_surveys/random_sample"
    merged_result = process_and_merge_folder(folder_path)
    print(merged_result.head())