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
Labeling one image takes about 2 minutes. 

1. Move the timelapse curser to the most recent image
2. Move it back in time until you find an image that is in a dry season month (for Zambia, 6-10), has no clouds, and is in 2016 or later. 
3. Label this image. 
4. Continue this process until all eligible images have been labeled.

### Exporting Labels
Once you have labeled the locations in your survey, use the "Export Collected Data" button in the Collect Earth Launcher to retrieve your labels. 
