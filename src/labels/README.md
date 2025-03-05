# Earth Collect Labeling Guide

## Overview
This document provides guidance on using **Earth Collect** to create labels based on high-resolution imagery. Earth Collect integrates with Google Earth Pro, enabling manual annotation of sampled locations. This guide explains how to prepare input files, perform annotations, and integrate the output with the sampling and feature extraction workflows.

## Prerequisites
- **Google Earth Pro**: This software allows you to view and annotate high resolution imagery taken at multiple times across the world. Download and install Google Earth Pro from the [official website](https://www.google.com/earth/about/versions/).
- **Open Foris Collect**: This software is used to create and manage the labeling design. Download and install Open Foris Collect from the [official website](https://openforis.org/solutions/collect/).
- **Earth Collect**: Earth Collect takes in a survey created using Collect and administers it through Google Earth Pro. Download and install Earth Collect from the [official website](https://openforis.org/solutions/collect-earth/).

## Setting up your Open Foris Earth Collect Survey

### Creating a survey in Open Foris Collect
To create a new survey, launch Open Foris Collect. Use the Survey Designer to create a survey using the "Earth Collect" template. Export this survey.

### Modifying the bounding box sizes and sampling locations
The survey is exported as a `.cep` file. This file's extenstion can be changed to `.zip` and can then be unzipped and modified to follow the specifications you would like, e.g. how big you want the bounding box to be (see project_definition.properties) and the list of locations you would like to sample (see test_samples.ced). For example, if you want the bounding boxes to be 1km across, the `distance_to_plot_boundaries` variable should be set to 500, since this indicates that the center point will be 500 meters to the boundary. 

Additionally, the survey will include some test locations, which are example locations that the survey can be tested on in Google Earth Pro. These can be replaced by a .csv of locations created in the sampling section of this repository such that the survey may be used to collect data over them. 

Once the survey is modified, it can be zipped back up and imported into Collect Earth (`Files > Import CEP` file and then choose `Files of Type: All Types` so it finds your `.zip` file). Make sure that when zipping you zip the *files* together, not the folder containing all the files, otherwise Collect Earth will not be able to open it properly. 

## Labeling with Earth Collect in Google Earth Pro

### Loading the survey into Google Earth Pro
Once the survey is ready with all the correct specificiations and locations that you would like to collect data over, launch the Collect Earth Launcher. This will automatically open Google Earth Pro as well. To load in the survey, click on File > Import CEP, and then search for the survey in All Files since Collect Earth will have trouble recognizing your survey once it has been modified. This will open up your survey in Google Earth Pro. 

### Labeling guidelines

#### Technical overview
Labeling one image takes about 1-10 minutes. The time it takes is dependent on how many valid images and irrigated plots are found. 

1. Click on the id of the first location you want to label in the left hand sidebar.
2. Move the timelapse cursor to the most recent image. It is important to do this for every new location, otherwise the time listed will be incorrect. 
3. Move it back in time until you find an image that is in a dry season month (for Zambia, 6-10), has no clouds, is not split, and is in 2016 or later. If there are no such images, submit the empty survey and move on. 
4. If you find a valid image, click on the area being labeled to pull up the survey. Fill out "Year 1".
5. If you find areas that you suspect are irrigated (see below for a detailed guide for determining whether an area should be considered irrigated), use the polygon function to outline each of these.
   a. If a polygon strays outside of the annotation area, outline the entire polygon. 
   b. Name the polygon according to the format `INITIALS_locationID_year` (e.g. `AB_3_2019`). All polygons in the same image and same year will have the same name. *[Or is it easier for them to have a unique id for each polygon? I was kind of loosing track]*
   c. Make sure to choose 0% opacity for the fill so that you can continue to see the area underneath during future years, and pick a specific color for this year in order to not confuse it with past years.
   d. If you are unsure about whether a polygon you have made is truly irrigated, describe why in the description. Otherwise, leave the description blank. 
7. Continue this process until all eligible images have been labeled, filling out as many of the "Year" tabs in the survey as is necessary. Make sure to change the color of your polygons with each year in order to avoid confusion *[Should we enforce what colors they use for each year?]*
8. Submit the survey and move on to the next area to be labeled.

#### Identifying smallholder irrigated areas

### Exporting Labels
Once you have labeled the locations in your survey, use the "Export Collected Data" button in the Collect Earth Launcher to retrieve your labels. If you have also placed pin locations for areas likely to represent smallholder irrigation, you can also export these as a `.kml` file as a redundancy. 
