# This script takes in a survey response file that you download from Earth Collect and turns it into a usable csv. 

import os
import xml.etree.ElementTree as ET
import pandas as pd
import shutil

def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    # Extract site-level information
    site_id = root.find("id/value").text if root.find("id/value") is not None else None
    x = root.find("location/x").text if root.find("location/x") is not None else None
    y = root.find("location/y").text if root.find("location/y") is not None else None
    operator = root.find("operator/value").text if root.find("operator/value") is not None else None
    plot_file = root.find("plot_file/value").text if root.find("plot_file/value") is not None else None
    internal_id = int(os.path.splitext(os.path.basename(file_path))[0]) # The filename without extension

    records = []
    # Iterate over potential day records (assuming up to 10 as in your XML)
    for i in range(1, 11):
        year_elem = root.find(f"year{i}")
        month_elem = root.find(f"month{i}")
        day_elem = root.find(f"day{i}")
        irrigation_elem = root.find(f"irrigation{i}")

        # Only create a row if there’s a valid year (adjust the check as needed)
        if year_elem is not None and year_elem.find("code") is not None:
            year = year_elem.find("code").text
            month = month_elem.find("code").text if (month_elem is not None and month_elem.find("code") is not None) else None
            day = day_elem.find("value").text if (day_elem is not None and day_elem.find("value") is not None) else None
            irrigation = irrigation_elem.find("code").text if (irrigation_elem is not None and irrigation_elem.find("code") is not None) else None

            records.append({
                "site_id": site_id,
                "internal_id": internal_id, 
                "plot_file": plot_file,
                "operator": operator,
                "x": x,
                "y": y,
                "image_number": i,
                "year": year,
                "month": month,
                "day": day,
                "irrigation": irrigation,
            })
    return records

def process_xml_zip(xml_zip):

    # Unzip the folder
    xml_folder = os.path.splitext(xml_zip)[0]
    shutil.unpack_archive(xml_zip, xml_folder)

    xml_folder = xml_folder + '/1' # move into the "1" folder

    all_records = []
    for filename in os.listdir(xml_folder):
        if filename.endswith(".xml"):
            file_path = os.path.join(xml_folder, filename)
            all_records.extend(parse_xml(file_path))

    # Create a DataFrame and export to CSV
    df = pd.DataFrame(all_records)
    output_csv = xml_folder + ".csv"
    df.to_csv(output_csv, index=False)
    print(f"CSV successfully created at: {output_csv}")
    
    return all_records

if __name__ == '__main__':

    xml_zip = "data/labels/test/AnnaBoser_collectedData_earthirrigation_survey_3_6_on_140325_183804_ZIP_WITH_XML.zip"
    
    all_records = process_xml_zip(xml_zip)
