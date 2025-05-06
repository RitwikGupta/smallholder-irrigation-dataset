import sys
import os
import zipfile
import shutil

# Add the project root to the system path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.utils.utils import get_data_root, save_data

def generate_surveys(survey_name, sample_group):
    """
    For each sample in the sample group without an associated survey,
    generate a survey with modified project properties.
    """
    data_root = get_data_root()
    survey_template_path = os.path.join(data_root, "labels/survey_template", survey_name)
    sample_group_path = os.path.join(data_root, "sampling/samples", sample_group)
    survey_group_path = os.path.join(data_root, "labels/unlabeled_surveys", sample_group)

    samples = [s.removesuffix(".csv") for s in os.listdir(sample_group_path) if s.endswith('.csv')]

    for sample in samples:
        output_zip_path = os.path.join(survey_group_path, f"{sample}.zip")
        if os.path.exists(output_zip_path):
            print(f"Survey for {sample} already exists. Skipping.")
            continue

        print(f"Generating survey for {sample}")
        generate_survey(survey_template_path, survey_group_path, sample_group_path, sample)


def generate_survey(template_zip_path, output_dir, sample_dir, sample_name):
    """
    Generate a survey based on the Open Foris Collect survey file and the sample group.

    Specifically, the returned survey will be a zipped file which contains all the same files as contained in the survey template, 
    except it will also contain a copy of the sample and have a modified project_definition.properties file where: 
        distance_to_plot_boundaries=500
        csv=${project_path}/'the sample's name'
    This file will have the same name as the sample it contains. 

    Parameters:
        survey_path (str): Path to the Open Foris Collect survey file.
        sample_group_path (str): Path to the sample group.
        sample (str): Sample name to generate the survey for.
    """
    temp_dir = os.path.join(output_dir, f"temp_{sample_name}")
    os.makedirs(temp_dir, exist_ok=True)

    # Unzip template into temp_dir
    with zipfile.ZipFile(template_zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    prop_path = os.path.join(temp_dir, "project_definition.properties")

    # Desired values
    distance_line = "distance_to_plot_boundaries=500\n"
    csv_line = f"csv=${{project_path}}/{sample_name}.csv\n"

    # Read original lines
    with open(prop_path, 'r') as f:
        lines = f.readlines()

    # Replace lines if they exist
    new_lines = []
    for line in lines:
        if line.startswith("distance_to_plot_boundaries="):
            new_lines.append(distance_line)
            found_distance = True
        elif line.startswith("csv="):
            new_lines.append(csv_line)
            found_csv = True
        else:
            new_lines.append(line)

    # Write updated file
    with open(prop_path, 'w') as f:
        f.writelines(new_lines)

    # Copy the sample file into the directory
    sample_file_path = os.path.join(sample_dir, f"{sample_name}.csv")
    shutil.copy(sample_file_path, os.path.join(temp_dir, f"{sample_name}.csv"))

    # Zip everything in temp_dir into the final zip
    output_zip_path = os.path.join(output_dir, f"{sample_name}.zip")
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for foldername, _, filenames in os.walk(temp_dir):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)

    # Clean up
    shutil.rmtree(temp_dir)
    print(f"Survey for {sample_name} written to {output_zip_path}")


if __name__ == "__main__":

    # Example usage/test

    # survey_name = "irrigation_survey_3_6_published_20250411T143124.zip" 
    # sample_group = "random_sample"

    # generate_surveys(survey_name, sample_group)

    import argparse

    parser = argparse.ArgumentParser(description="Generate surveys for a sample group.")
    parser.add_argument("survey_name", type=str, help="Name of the survey template zip file.")
    parser.add_argument("sample_group", type=str, help="Name of the sample group directory.")
    args = parser.parse_args()
    generate_surveys(args.survey_name, args.sample_group)
