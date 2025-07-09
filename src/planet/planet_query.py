import asyncio
from datetime import datetime, timedelta
from planet import Auth, Session, DataClient, data_filter
import geopandas as gpd
from shapely.geometry import mapping, shape
from tqdm.asyncio import tqdm
import tqdm.asyncio

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

async def search_single_feature(client, feature_idx, row, total_features, pbar):
    """Search Planet imagery for a single feature"""
    geometry = fix_geometry_coordinates(mapping(row.geometry))
    
    feature_date = datetime(
        year=int(row['year']),
        month=int(row['month']),
        day=int(row['day']),
        hour=12
    )
    
    # Create combined date string
    date_str = f"{row['year']}-{row['month']:02d}-{row['day']:02d}"
    
    try:
        # Create filters
        geom_filter = data_filter.geometry_filter(geometry)
        
        # Filter for +/- 15 days around the label date
        date_range_filter = data_filter.date_range_filter(
            "acquired",
            feature_date - timedelta(days=15),
            feature_date + timedelta(days=15)
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
            name=f"search_{row['site_id']}",
            search_filter=combined_filter,
            item_types=["PSScene"]
        )

        items = []
        async for item in search_results:
            item['feature_metadata'] = {
                'site_id': row['site_id'],
                'internal_id': row['internal_id'],
                'date': feature_date.isoformat() + 'Z',
                'irrigation': row['irrigation'],
                'percent_coverage': row['percent_coverage']
            }

            item['site_id'] = row['site_id']
            item['feature_date'] = date_str
            items.append(item)
        
        filtered_items = filter_by_coverage(items, geometry, min_coverage=100)

        pbar.set_postfix(
            {
                'Total Found': len(items),
                'Full Coverage': len(filtered_items),
                'Feature': f"{feature_idx + 1}/{total_features}"
            },
            refresh=True
        )
        pbar.update(1)
            
        return filtered_items
        
    except Exception as e:
        pbar.write(f"Error processing feature {feature_idx + 1}: {str(e)}")
        import traceback
        pbar.write(traceback.format_exc())
        pbar.update(1)
        return []

async def search_planet_imagery():
    gdf = gpd.read_file('../data/labels/labeled_surveys/random_sample/latest_irrigation_data.geojson')
    
    auth = Auth.from_key(api_key)
    
    async with Session(auth=auth) as sess:
        client = DataClient(sess)
        
        # Process in batches of 10 to avoid overwhelming the API
        BATCH_SIZE = 10
        all_results = []

        n_batches = (len(gdf) + BATCH_SIZE - 1) // BATCH_SIZE
        with tqdm.tqdm(total=n_batches, desc="Processing batches", position=0) as batch_pbar:
            for batch_start in range(0, len(gdf), BATCH_SIZE):
                batch_end = min(batch_start + BATCH_SIZE, len(gdf))
                batch_size = batch_end - batch_start

                with tqdm.tqdm(total=batch_size, 
                             desc=f"Batch {batch_start//BATCH_SIZE + 1}/{n_batches}",
                             position=1, 
                             leave=False) as feature_pbar:

                    tasks = [
                        search_single_feature(
                            client, idx, row, len(gdf), feature_pbar
                        )
                        for idx, row in gdf.iloc[batch_start:batch_end].iterrows()
                    ]
                    
                    batch_results = await asyncio.gather(*tasks)
                    
                    for results in batch_results:
                        all_results.extend(results)
                    
                    batch_pbar.set_postfix(
                        {'Full Coverage Images': len(all_results)},
                        refresh=True
                    )
                    batch_pbar.update(1)

        with open('planet_search_results.json', 'w') as f:
            import json
            json.dump(all_results, f, indent=2)
        
        print(f"\nSearch complete. Found {len(all_results)} images with full coverage")

if __name__ == "__main__":
    # Enable asyncio for jupyter if we're in a notebook
    try:
        import nest_asyncio
        nest_asyncio.apply()
    except ImportError:
        pass
    
    asyncio.run(search_planet_imagery())