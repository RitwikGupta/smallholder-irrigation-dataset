# functions to read in agricultural data, resample to 1km, and save the grid's lat/lon coordinates as a csv with info on agriculture and country

# Does NOT include elevation/aspect/slope data yet. 

import sys
import os

# Add the project root to the system path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Now import the module
from src.utils.utils import get_data_root, save_data

import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling, transform_geom
import numpy as np
import pandas as pd
import pyproj
import matplotlib.pyplot as plt
import geopandas as gpd
import re

def get_utm_crs(lon, lat):
    """Returns the EPSG code for the appropriate UTM zone based on longitude and latitude."""
    zone = int((lon + 180) / 6) + 1
    if lat >= 0:
        epsg_code = 32600 + zone  # Northern Hemisphere
    else:
        epsg_code = 32700 + zone  # Southern Hemisphere
    return pyproj.CRS.from_epsg(epsg_code)

def resample_agriculture_data(src_path, res):
    """
    Resample the GFSAD agriculture raster dataset (orginical resolution approximately 30m) 
    to a specified resolution (in meters) and return the lat/lon coordinates
    of the resampled grid points with the proportion of pixels with value == 2 (cropland). 

    Zero values are removed, retaining only pixels with at least some cropland.

    Parameters:
        src_path (str): Path to the source raster file.
        res (int): Resolution in meters for the resampled raster.
    """

    with rasterio.open(src_path) as src:
        print("Original CRS:", src.crs)
        print("Original Bounds:", src.bounds)
        print("Original Resolution:", src.res)

        # Read the original raster
        data = src.read(1)

        # Create binary mask where value == 2
        binary_mask = (data == 2).astype(np.uint8)
        print("Binary mask created. Non-zero count:", np.count_nonzero(binary_mask))

        # # Plot original binary mask
        # plt.figure(figsize=(8, 6))
        # plt.title('Binary Mask (Value == 2)')
        # plt.imshow(binary_mask, cmap='gray')
        # plt.colorbar(label='Binary Values')
        # plt.show()

        # Determine UTM CRS based on the raster's center
        center_lon = (src.bounds.left + src.bounds.right) / 2
        center_lat = (src.bounds.top + src.bounds.bottom) / 2
        utm_crs = get_utm_crs(center_lon, center_lat)
        print("UTM CRS Selected:", utm_crs)

        # Calculate the new transform and dimensions for the specified resolution
        transform, width, height = rasterio.warp.calculate_default_transform(
            src.crs, utm_crs, src.width, src.height, *src.bounds, resolution=(res, res)
        )
        print("Resampled Dimensions:", width, height)

        # Prepare an empty array for the resampled raster
        resampled_raster = np.empty((height, width), dtype=np.float32)

        # Reproject and resample in memory using average resampling
        rasterio.warp.reproject(
            source=binary_mask,
            destination=resampled_raster,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=transform,
            dst_crs=utm_crs,
            resampling=rasterio.warp.Resampling.average
        )

        # # Plot resampled raster
        # plt.figure(figsize=(8, 6))
        # plt.title('Resampled Raster (Proportion of Value == 2)')
        # plt.imshow(resampled_raster, cmap='viridis')
        # plt.colorbar(label='Proportion of Pixels with Value 2')
        # plt.show()

    # Extract UTM coordinates (center of each pixel)
    rows, cols = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')
    xs, ys = rasterio.transform.xy(transform, rows, cols, offset='center')

    # Convert UTM coordinates to WGS84 (latitude, longitude)
    transformer = pyproj.Transformer.from_crs(utm_crs, "EPSG:4326", always_xy=True)
    longitudes, latitudes = transformer.transform(np.array(xs).flatten(), np.array(ys).flatten())

    # # Debug: Plot points to verify geolocation
    # plt.figure(figsize=(8, 6))
    # plt.scatter(longitudes, latitudes, c=resampled_raster.flatten(), cmap='viridis', s=1)
    # plt.colorbar(label='Proportion of Value == 2')
    # plt.title('Reprojected Points (WGS84)')
    # plt.xlabel('Longitude')
    # plt.ylabel('Latitude')
    # plt.show()

    # Flatten values for DataFrame
    values = resampled_raster.flatten()

    # Create DataFrame with lat/lon
    df = pd.DataFrame({
        'latitude': latitudes,
        'longitude': longitudes,
        'agriculture': values
    })

    # Filter out zero values
    df = df[df['agriculture'] > 0]

    return df

def add_country(df):
    """
    Given a DataFrame with lat/lon coordinates, add a column with the country name.
    """

    # Load country boundaries
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # Create a GeoDataFrame from the DataFrame
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))

    # Perform a spatial join
    gdf = gpd.sjoin(gdf, world, how='left', op='within')

    # rename the 'name' column to 'country'
    gdf.rename(columns={'name': 'country'}, inplace=True)

    # Only keep latitude, longitude, agriculture, and country columns
    gdf = gdf[['latitude', 'longitude', 'agriculture', 'country']]

    return pd.DataFrame(gdf)

def process_and_combine_ag_data(ag_data_loc, res):
    """
    Process the agricultural data and combine with country information.
    """

    # Get a list of all tif files at ag_data_loc
    files = [f for f in os.listdir(ag_data_loc) if f.endswith('.tif')]

    # Initialize an empty DataFrame
    full_df = pd.DataFrame()

    # for each file, resample the data and add country information. 
    for file in files:
        df = resample_agriculture_data(ag_data_loc + file, res)
        df = add_country(df)
        filename, _ = os.path.splitext(file)
        save_data(df, f'sampling/grid/{filename}.csv', description=f'Agriculture Data Resampled to {res}m Grid', file_format='csv')

        # Combine the data
        full_df = pd.concat([full_df, df])

    return full_df

def add_id(df):
    """
    Add a unique ID to the DataFrame.
    """

    # Add a unique ID
    df['id'] = ['id_' + str(i) for i in range(len(df))]

    # Make ID the first column
    df = df[['id'] + [col for col in df.columns if col != 'id']]

    return df
    

if __name__ == '__main__':

    ag_data_loc = get_data_root() + '/sampling/raw/GFSAD/GFSAD30AFCE_001-20250206_011249/'
    df = process_and_combine_ag_data(ag_data_loc, 1000) # 1km resolution
    df = add_id(df)

    # Save the data
    save_data(df, 'sampling/grid/combined/agriculture_grid.csv', description='Agriculture Data Resampled to 1km Grid', file_format='csv')