# Earth Collect Labeling Guide

## Overview

This folder contains tools and instructions for labeling smallholder irrigation using **Earth Collect** and **Google Earth Pro**, as part of a broader effort to build a machine learning benchmark dataset for dry season irrigation in Zambia. 

📃 **Refer to the full labeling protocol here**:  
[📝 Labeling Guide (Google drive link)](https://docs.google.com/document/d/1F-5uTBTCsP3ZU5hwj1NE4RYbmBofbXzeytcCKIT6iz8/edit?usp=sharing)

This README complements the guide with technical instructions and script documentation.

---

## Software prerequisites

- **Google Earth Pro** provides access to historical high-resolution imagery. Download and install Google Earth Pro from the [official website](https://www.google.com/earth/about/versions/)
- **Open Foris Collect + Earth Collect** allow structured data collection across 
  - **Open Foris Collect**: This software is used to create and manage the labeling design. The survey used in this project was created using this tool and can be found in the folder `data/labels/survey_template/irrigation_survey_3_6_published_20250411T143124.zip`. If you are just using this already created survey, you do not need to download Open Foris Collect. To create your own survey, download and install Open Foris Collect from the [official website](https://openforis.org/solutions/collect/).
  - **Earth Collect**: Earth Collect takes in a survey created using Collect and administers it through Google Earth Pro. Download and install Earth Collect from the [official website](https://openforis.org/solutions/collect-earth/).


---

## Generating surveys

To create a survey to label, you will need: 
1. A survey template, saved in `data/labels/survey_template/` (e.g. `irrigation_survey_3_6_published_20250411T143124.zip`)
2. Sample location file(s) created using `src/sampling/`, stored in `data/sampling/samples/<SAMPLE-GROUP-NAME>`

To generate surveys that can be read into Earth Collect/Google Earth Pro, you can use `surveys_with_locations.py`, which will generate surveys for each location file in your sample group folder and save them in the `data/labels/unlabeled_surveys/<SAMPLE-GROUP-NAME>` folder. Note this script will also change the bounding box size to 1km in all surveys. 

Example usage for the `random_sample` sample group:

```bash
python surveys_with_locations.py --survey_name irrigation_survey_3_6_published_20250411T143124.zip --sample_group random_sample
```

More information on what exactly is being changed in the survey template when this command is run: 

### Modifying the bounding box sizes and sampling locations
The survey is exported as a `.cep` file. This file's extenstion can be changed to `.zip` and can then be unzipped and modified to follow the specifications you would like, e.g. how big you want the bounding box to be and the list of locations you would like to sample. 

Specifically, to change the bounding boxes to be 1km across, modify the `distance_to_plot_boundaries` variable in the `project_definition.properties` file to to 500, since this indicates that the center point will be 500 meters to the boundary. 

Additionally, the survey will include some test locations, which are example locations that the survey can be tested on in Google Earth Pro (see `test_samples.ced`). You can provide your own locations, for example a `.csv` generated using the files in the `sampling` section in this repository). To do so, add the `.csv` file to the folder and modify the `csv` variable in the `project_definition.properties` to by replacing "test_samples.ced" with the name of the new `.csv` file you added. 

Once the survey is modified, it can be zipped back up and imported into Collect Earth (`Files > Import CEP` file and then choose `Files of Type: All Types` so it finds your `.zip` file). Make sure that when zipping you zip the *files* together, not the folder containing all the files, otherwise Collect Earth will not be able to open it properly. 

---

# Generating and exporting labels

Load in and fill out the survey in Earth Collect/Google Earth Pro. The survey responses can be exported as a zip file in Earth Collect, and polygons can be placed in a folder and exported as a .kml file in Google Earth Pro. 

For more information on generating and exporting labels, please refer to the [📝 Labeling Guide](https://docs.google.com/document/d/1F-5uTBTCsP3ZU5hwj1NE4RYbmBofbXzeytcCKIT6iz8/edit?usp=sharing)
