# Earth Collect Labeling Guide

## Overview
This document provides guidance on using **Earth Collect** to create labels based on high-resolution imagery. Earth Collect integrates with Google Earth Pro, enabling manual annotation of sampled locations. This guide explains how to prepare input files, perform annotations, and integrate the output with the sampling and feature extraction workflows.

## Prerequisites
- **Google Earth Pro**: This software allows you to view and annotate high resolution imagery taken at multiple times across the world. Download and install Google Earth Pro from the [official website](https://www.google.com/earth/about/versions/).
- **Open Foris Collect**: This software is used to create and manage the labeling design. Download and install Open Foris Collect from the [official website](https://openforis.org/solutions/collect/).
- **Earth Collect**: Earth Collect takes in a survey created using Collect and administers it through Google Earth Pro. Download and install Earth Collect from the [official website](https://openforis.org/solutions/collect-earth/).

## Creating a survey in Open Foris Collect
To create a survey, launch Open Foris Collect. Use the Survey Designer to create a survey using the "Earth Collect" template. 

## Modifying the bounding box sizes and sampling locations
The survey can be exported as a `.cep` file. This file's extenstion can be changed to `.zip` and can then be unzipped and modified to follow the specifications you would like, e.g. how big you want the bounding box to be (see project_definition.properties) and the list of locations you would like to sample (see test_samples.ced). Once the survey is modified, it can be zipped back up and imported into Collect Earth (`Files > Import CEP` file and then choose `Files of Type: All Types` so it finds your `.zip` file) Wake sure that when zipping you zip the *files* together, not the folder containing all the files, otherwise Collect Earth will not be able to open it properly. 


