import sys
import os

# Add the project root to the system path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Now import the module
from src.utils.utils import get_data_root, save_data

import rasterio
import numpy as np
import pandas as pd
import pyproj
import matplotlib.pyplot as plt

def sample_grid(grid, num_samples, ag_thresh=0):
    """
    Sample a grid of points from a raster dataset, returning the coordinates
    of the sampled points and the values of the raster at those points.

    Parameters:
        grid (str): The path to the grid CSV file.
        num_samples (int): The number of samples to take.
        ag_thresh (int): The agriculture threshold value.

    Returns:
        pd.DataFrame: A DataFrame containing the sampled points and values.
    """
    # Load the grid
    grid = pd.read_csv(grid)

    # Sample the grid without replacement
    samples = grid.sample(num_samples)
    samples = samples[samples['value'] > ag_thresh]

    # Format the grid to be used with Collect
    # Remove the 'value' column
    samples = samples.drop(columns=['value'])

    # Rename columns
    samples = samples.rename(columns={'latitude': 'YCoordinate', 'longitude': 'XCoordinate'})

    # Add unique IDs
    samples.insert(0, 'id', [f'id_{i}' for i in range(1, len(samples) + 1)])

    # Add topographic columns with zeros
    samples['elevation'] = 0
    samples['slope'] = 0
    samples['aspect'] = 0

    return samples

if __name__ == '__main__':

    grid_loc = get_data_root() + '/sampling/grid/agriculture_grid_S20E20.csv' 

    # Sample the grid
    samples = sample_grid(grid_loc, 100)

    # Save the samples
    save_data(samples, 'sampling/samples/sample_grid.csv', description='100 Sampled grid points from agriculture_grid_S20E20', file_format='csv')