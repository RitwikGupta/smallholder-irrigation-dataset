import pandas as pd
import geopandas as gpd
from shapely.ops import unary_union
from utils.geometries import survey_polygon
from typing import Optional
from shapely.validation import make_valid
import os

def merge_and_check(survey_path: str, polygons_path: Optional[str] = None):
    """
    Loads in and merges survey data with polygon data, performs consistency checks, and calculates percent coverage.
    This function processes survey data and polygon data to ensure consistency between the two datasets.
    It performs a series of checks to validate the relationship between survey rows and polygons, 
    calculates the percentage of survey area covered by polygons, and generates a report of any issues found.
    Args:
        survey (pd.DataFrame): A DataFrame containing survey data with columns:
            - internal_id: Unique identifier for the survey.
            - year, month, day: Date of the survey.
            - irrigation: Irrigation status (1 = no irrigation, 2-5 = varying levels of irrigation certainty).
            - x (longitude), y (latitude): Coordinates of the survey location.
        polygons (gpd.GeoDataFrame): A GeoDataFrame containing polygon data with columns:
            - internal_id: Unique identifier for the polygon.
            - year, month, day: Date associated with the polygon.
            - geometry: Polygon geometry.
            - certainty: Certainty level of the polygon (1-5).
    Returns:
        gpd.GeoDataFrame: A GeoDataFrame containing the survey data with additional columns:
            - percent_coverage: Percentage of the survey area covered by polygons.
            - percent_coverage_high_certainty: Percentage of the survey area covered by polygons with certainty >= 4.
            - poly_avg_size: Average size of the polygons covering the survey area.
            - poly_avg_size_high_certainty: Average size of the polygons with certainty >= 4.
    Raises:
        ValueError: If the input data does not meet the expected format or contains invalid values.
    Notes:
        - The function generates a report of any inconsistencies or issues found during processing.
        - The report is printed to the console and includes details such as unmatched polygons, 
          mismatched irrigation statuses, and polygons that do not overlap survey areas.
        - Polygons are matched to survey rows based on spatial intersection and matching attributes 
          (internal_id, year, month, day).
    Example:
        survey = pd.DataFrame({...})
        polygons = gpd.GeoDataFrame({...})
        result = merge_and_check(survey, polygons)
    """

    # Load the survey and polygon data.
    survey = pd.read_csv(survey_path)
    if polygons_path:
        polygons = gpd.read_file(polygons_path)
    else: 
        polygons = gpd.read_file(survey_path.replace(".csv", ".geojson"))

    # Initialize the report as a list of strings.
    report = []

    # Add new columns for percent coverage and polygon average size
    survey["percent_coverage"] = 0.0
    survey["percent_coverage_high_certainty"] = 0.0
    survey["poly_avg_size"] = None
    survey["poly_avg_size_high_certainty"] = None

    # For area calculations we need a geometry for each survey row.
    # The survey CSV includes columns: internal_id, year, month, day, irrigation, x (lon), and y (lat).

    survey["geometry"] = survey.apply(survey_polygon, axis=1)
    survey_gdf = gpd.GeoDataFrame(survey, geometry="geometry", crs="EPSG:4326")

    # We will add a column for the overall location id to the geojson too
    # This will help us ensure that all polygons get matched to a location
    polygons["site_id"] = None 

    # Process each survey row
    for idx, row in survey_gdf.iterrows():

        # Find polygons that match by internal_id (or site_id if the labeler accidentally used that), year, month, and day.
        condition = (
            ((polygons["internal_id"] == row["internal_id"]) | 
             (polygons["internal_id"] == int(row["site_id"][3:]))) &
            (polygons["year"] == row["year"]) &
            (polygons["month"] == row["month"]) &
            (polygons["day"] == row["day"])
        )
        matching_polys = polygons[condition].copy()

        # Get irrigation value and perform checks.
        irrigation = int(row["irrigation"])

        # Check 1: If irrigation == 1, there should be no polygons.
        if irrigation == 1 and not matching_polys.empty:
            report.append(f"Row {idx} (internal_id {row['internal_id']}, {row['day']}/{row['month']}/{row['year']}): survey marked irrigation as 1 (no irrigation) but found {len(matching_polys)} matching polygon(s).")
        # Check 2: If irrigation > 1, there should be at least one polygon.
        if irrigation is not None and irrigation > 1 and matching_polys.empty:
            report.append(f"Row {idx} (internal_id {row['internal_id']}, {row['day']}/{row['month']}/{row['year']}): survey marked irrigation {irrigation} (possible irrigation) but no matching polygons found.")
        # Check 3: If irrigation == 5, at least one polygon should have certainty == 5.
        if irrigation == 5:
            if matching_polys.empty or (matching_polys["certainty"].max() < 5):
                report.append(f"Row {idx} (internal_id {row['internal_id']}, {row['day']}/{row['month']}/{row['year']}): survey marked irrigation 5 (definitely irrgation) but no polygon with certainty 5 found.")
        # Check 4: If irrigation == 2, 3, or 4, all matched polygons should have certainty <= 4.
        if irrigation in [2, 3, 4]:
            if not matching_polys.empty and matching_polys["certainty"].max() > 4:
                report.append(f"Row {idx} (internal_id {row['internal_id']}, {row['day']}/{row['month']}/{row['year']}): survey marked irrigation {irrigation} (uncertain) but found a polygon with certainty 5 (certain).")

        # Add the site_id to matched polygons
        if not matching_polys.empty:
            polygons.loc[condition, "site_id"] = row["site_id"]

        # Compute percent coverage.
        survey_area = row["geometry"].area
        if not matching_polys.empty:
            # Clean the geometries to ensure they are valid
            matching_polys.geometry = [make_valid(geom) for geom in matching_polys.geometry]

            # Check that all polygons are at least partially overlapping the survey area
            # If not, list it in the report
            for poly_idx, poly in matching_polys.iterrows():
                if not row["geometry"].intersects(poly["geometry"]):
                    report.append(f"Polygon {poly_idx} (internal_id {poly['internal_id']}, {poly['day']}/{poly['month']}/{poly['year']}) does not overlap the survey area.")
            
            # Calculate the average size of the polygons in square meters (use local CRS)
            avg_size = matching_polys.to_crs("EPSG:32735").geometry.area.mean() if not matching_polys.empty else None
            
            # Calculate the overlap
            union_all = unary_union(matching_polys.geometry)
            intersection_all = row["geometry"].intersection(union_all)
            percent_total = (intersection_all.area / survey_area) * 100 if survey_area > 0 else 0.0

            # For high-certainty coverage, filter for certainty >= 4.
            high_polys = matching_polys[matching_polys["certainty"] >= 4]

            # Calculate the average size of the high-certainty polygonss in square meters (use local CRS)
            avg_size_high = high_polys.to_crs("EPSG:32735").geometry.area.mean() if not high_polys.empty else None

            # Calculate the coverage/overlap for high-certainty polygons
            if not high_polys.empty:
                union_high = unary_union(high_polys.geometry.tolist())
                intersection_high = row["geometry"].intersection(union_high)
                percent_high = (intersection_high.area / survey_area) * 100 if survey_area > 0 else 0.0
            else:
                percent_high = 0.0
        else:
            percent_total = 0.0
            percent_high = 0.0
            avg_size = None
            avg_size_high = None

        survey_gdf.at[idx, "percent_coverage"] = percent_total
        survey_gdf.at[idx, "percent_coverage_high_certainty"] = percent_high
        survey_gdf.at[idx, "poly_avg_size"] = avg_size
        survey_gdf.at[idx, "poly_avg_size_high_certainty"] = avg_size_high

    # After processing all survey rows, check for any polygons that were not matched.
    unmatched_polys = polygons[~polygons["site_id"].notnull()]
    for poly_idx, poly in unmatched_polys.iterrows():
        report.append(f"Polygon {poly_idx} (internal_id {poly['internal_id']}, {poly['day']}/{poly['month']}/{poly['year']}) has no matching survey row.")

    # Output the report.
    print("----- CHECK REPORT -----")
    if report:
        for line in report:
            print(line)
    else:
        report.append("All checks passed successfully.")
        print(report[0])

    # Save the report
    merged_folder = os.path.join(os.path.dirname(os.path.dirname(survey_path)), "merged")
    os.makedirs(merged_folder, exist_ok=True)
    report_path = os.path.join(merged_folder, os.path.basename(survey_path).replace(".csv", "_report.txt"))
    with open(report_path, "w") as f:
        for line in report:
            f.write(line + "\n")
    print(f"Saved report at {report_path}")

    # Save  the updated survey results to a CSV, dropping geometry
    survey_gdf["source_file"] = os.path.basename(survey_path).replace(".csv", "")
    survey_results = survey_gdf.copy()
    results_path = os.path.join(merged_folder, os.path.basename(survey_path).replace(".csv", "_merged.csv"))
    survey_results.drop(columns="geometry").to_csv(results_path, index=False)
    print(f"Saved merged dataset at {results_path}")

    # Return the survey results GeoDataFrame (with added percent coverage columns)
    return survey_gdf


if __name__ == "__main__":
    
    # Example usage/test code

    # survey = "data/labels/labeled_surveys/random_sample/processed/MV_76-100.csv"
    # survey_results = merge_and_check(survey)
    # print(survey_results.head())

    # CLI argument parsing

    import argparse

    parser = argparse.ArgumentParser(description="Merge survey data with polygon data and perform consistency checks.")
    parser.add_argument("survey_path", type=str, help="Path to the survey CSV file.")
    parser.add_argument("--polygons_path", type=str, help="Path to the polygons GeoJSON file (optional).")
    args = parser.parse_args()
    
    survey_path = args.survey_path
    polygons_path = args.polygons_path if args.polygons_path else None
    
    survey_results = merge_and_check(survey_path, polygons_path)
    
    print(f"Merged results have {len(survey_results)} rows.")
