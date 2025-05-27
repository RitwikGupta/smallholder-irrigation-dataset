import sys
import os
import pandas as pd

# Add the project root to the system path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Now import the module
from src.utils.utils import *
from src.utils.geometries import bounding_box
import geopandas as gpd
from shapely.geometry import box

group_name = "random_sample"
latest_irrigation_data = generate_latest_irrigation_data(group_name)

# Generate bounding boxes as Shapely geometries for each row
latest_irrigation_data['geometry'] = latest_irrigation_data.apply(
    lambda row: box(*bounding_box(row['y'], row['x'], half_side_km=0.5)), axis=1
)

# Convert the DataFrame to a GeoDataFrame
latest_irrigation_data_gdf = gpd.GeoDataFrame(latest_irrigation_data, geometry='geometry', crs="EPSG:4326")

# Save the GeoDataFrame to a GeoJSON file
geojson_path = "targeting/irrigation_data.geojson"
description = f"The latest labeled irrigation data"
save_data(latest_irrigation_data_gdf, geojson_path, description=description, file_format="json")