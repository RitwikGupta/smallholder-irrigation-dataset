## Sampling

This module handles spatial sampling workflows used to generate candidate locations for annotation. These locations define the inputs for labeling irrigation, to be used in `src/labels`.

### Overview

Sampling is performed in two main steps:

1. **Grid Creation**: A uniform sampling grid is generated across the defined area of interest.
2. **Grid Sampling**: A stratified or uniform subset of grid points is selected for labeling.

These steps produce a GeoJSON or GeoPackage containing points which represent the center of a tile to label using the workflow described in `src/labels`.

### Create a grid to sample from

- `make_grid.py`: Generates a regular grid of points over the study area. Grid spacing can be configured based on the desired resolution or number of samples.

For this project, we create a 1km grid across all agricultural lands in Africa according to the Global Food Security-support Analysis Data (GFSAD) Cropland Extent 2015 Africa 30 m V001. 


### Sample locations from the grid

- `sample_grid.py`: Use the sample generator to create a sampling group. Every time you sample using this group, you will draw without replacement from the grid. You can specify: 
    - The number of samples to draw
    - Whether you want to sample from all countries or only a subset
    - The fraction of the grid cell that must be agricultural land to be included in this sample