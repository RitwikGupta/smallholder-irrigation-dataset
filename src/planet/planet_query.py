import asyncio
from datetime import datetime, timedelta
from planet import Auth, Session, DataClient, data_filter
import geopandas as gpd
from shapely.geometry import mapping, shape
from tqdm.asyncio import tqdm
import tqdm.asyncio
import numpy as np
import argparse
import os
import json

# Read API key
with open('planet_api_key', 'r') as f:
    api_key = f.read().strip()

def fix_geometry_coordinates(geometry):
    """Fix coordinate order from [lat, lon] to [lon, lat]"""
    if geometry['type'] == 'Polygon':
        fixed_coords = [[[coord[1], coord[0]] for coord in ring] for ring in geometry['coordinates']]
        return {
            'type': 'Polygon',
            'coordinates': fixed_coords
        }
    return geometry

def filter_by_coverage(items, aoi_geometry, min_coverage=100):
    """
    Filter for coverage as documented by Planet here
    https://github.com/planetlabs/notebooks/blob/master/jupyter-notebooks/use-cases/crop-segmentation-and-classification/crop-segmentation/1-datasets-identify.ipynb
    """
    if not items:
        return []
    
    # Convert AOI to shapely
    aoi_shape = shape(aoi_geometry)
    
    filtered_items = []
    for item in items:
        try:
            footprint = shape(item['geometry'])
            overlap = 100.0 * (aoi_shape.intersection(footprint).area / aoi_shape.area)
            item['feature_metadata']['overlap_percent'] = overlap

            if overlap >= min_coverage:
                filtered_items.append(item)
        except Exception as e:
            print(f"Error calculating overlap for item {item.get('id', 'unknown')}: {str(e)}")
    
    return filtered_items

def select_evenly_spaced_images(items, n_desired=36):
    """
    Select up to n_desired images that are as evenly spaced as possible across the time range.
    """
    if not items:
        return []
    
    items = sorted(items, key=lambda x: x['properties']['acquired'])

    if len(items) <= n_desired:
        return items
    
    spacing = (len(items) - 1) / (n_desired - 1)
    indices = [int(round(i * spacing)) for i in range(n_desired)]
    indices = sorted(list(set(indices)))
    
    return [items[i] for i in indices]

async def search_single_feature(client, feature_idx, row, total_features, pbar, n_desired):
    """Search Planet imagery for a single feature"""
    geometry = fix_geometry_coordinates(mapping(row.geometry))
    
    feature_date = datetime(
        year=int(row['year']),
        month=int(row['month']),
        day=int(row['day']),
        hour=12
    )
    
    try:
        geom_filter = data_filter.geometry_filter(geometry)
        
        # Filter for +/- 182 days around the label date
        date_range_filter = data_filter.date_range_filter(
            "acquired",
            feature_date - timedelta(days=182),
            feature_date + timedelta(days=182)
        )

        # Filter for 0% cloud cover
        cloud_filter = data_filter.range_filter(
            "cloud_cover",
            gte=0,
            lte=0
        )
        
        instrument_filter = data_filter.string_in_filter(
            "instrument",
            ["PSB.SD"]  # PlanetScope Surface Reflectance
        )

        combined_filter = data_filter.and_filter([
            geom_filter,
            date_range_filter,
            cloud_filter,
            instrument_filter
        ])
        
        search_results = client.search(
            name=f"search_{row['unique_id']}",
            search_filter=combined_filter,
            item_types=["PSScene"]
        )

        items = []
        async for item in search_results:
            item['feature_metadata'] = {
                'unique_id': row['unique_id'],
                'internal_id': row['internal_id'],
                'date': feature_date.isoformat() + 'Z',
                'irrigation': row['irrigation'],
                'percent_coverage': row['percent_coverage']
            }

            item['unique_id'] = row['unique_id']
            items.append(item)
        
        filtered_items = filter_by_coverage(items, geometry, min_coverage=100)
        selected_items = select_evenly_spaced_images(filtered_items, n_desired=n_desired)

        pbar.set_postfix(
            {
                'Selected': len(selected_items),
                'Feature': f"{feature_idx + 1}/{total_features}"
            },
            refresh=True
        )
        pbar.update(1)
            
        return selected_items
        
    except Exception as e:
        pbar.write(f"Error processing feature {feature_idx + 1}: {str(e)}")
        import traceback
        pbar.write(traceback.format_exc())
        pbar.update(1)
        return []

async def search_planet_imagery(input_geojson, output_json, batch_size, n_desired):
    if not os.path.exists(input_geojson):
        raise FileNotFoundError(f"Input GeoJSON file not found: {input_geojson}")
        
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_json)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Ensure output file has .jsonl extension
    if not output_json.endswith('.jsonl'):
        output_json = output_json.rsplit('.', 1)[0] + '.jsonl'
    
    gdf = gpd.read_file(input_geojson)
    
    auth = Auth.from_key(api_key)
    
    total_images = 0
    total_features_with_images = 0
    
    async with Session(auth=auth) as sess:
        client = DataClient(sess)

        n_batches = (len(gdf) + batch_size - 1) // batch_size
        with tqdm.tqdm(total=n_batches, desc="Processing batches", position=0) as batch_pbar:
            for batch_start in range(0, len(gdf), batch_size):
                batch_end = min(batch_start + batch_size, len(gdf))
                current_batch_size = batch_end - batch_start

                with tqdm.tqdm(total=current_batch_size, 
                             desc=f"Batch {batch_start//batch_size + 1}/{n_batches}",
                             position=1, 
                             leave=False) as feature_pbar:

                    tasks = [
                        search_single_feature(
                            client, idx, row, len(gdf), feature_pbar, n_desired
                        )
                        for idx, row in gdf.iloc[batch_start:batch_end].iterrows()
                    ]
                    
                    batch_results = await asyncio.gather(*tasks)

                    with open(output_json, 'a') as f:
                        for results in batch_results:
                            if results:  # If we found any images for this feature
                                total_features_with_images += 1
                            for item in results:
                                json.dump(item, f)
                                f.write('\n')
                                total_images += 1
                    
                    batch_pbar.set_postfix(
                        {'Images': total_images, 'Features': total_features_with_images},
                        refresh=True
                    )
                    batch_pbar.update(1)

        print(f"\nSearch complete:")
        print(f"- Found {total_images} total images")
        print(f"- {total_features_with_images} out of {len(gdf)} features ({(total_features_with_images/len(gdf)*100):.1f}%) had images")
        print(f"- Average of {(total_images/total_features_with_images):.1f} images per feature with images")

def parse_args():
    parser = argparse.ArgumentParser(description='Search Planet imagery for labeled features')
    parser.add_argument('--input', '-i',
                      default='../../data/labels/labeled_surveys/random_sample/latest_irrigation_data.geojson',
                      help='Path to input GeoJSON file containing labeled features')
    parser.add_argument('--output', '-o',
                      default='planet_search_results.jsonl',
                      help='Path to output JSONL file for search results (will be converted to .jsonl extension)')
    parser.add_argument('--batch-size', '-b',
                      type=int,
                      default=10,
                      help='Number of features to process in each batch')
    parser.add_argument('--n-desired', '-n',
                      type=int,
                      default=36,
                      help='Number of desired images per feature')
    return parser.parse_args()

if __name__ == "__main__":
    # Enable asyncio for jupyter if we're in a notebook
    try:
        import nest_asyncio
        nest_asyncio.apply()
    except ImportError:
        pass
    
    args = parse_args()
    asyncio.run(search_planet_imagery(
        input_geojson=args.input,
        output_json=args.output,
        batch_size=args.batch_size,
        n_desired=args.n_desired
    ))