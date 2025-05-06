import xml.etree.ElementTree as ET
import json
import geopandas as gpd
import os

# Define the KML namespace
ns = {'kml': 'http://www.opengis.net/kml/2.2'}

def parse_name(name_text):
    """
    Parse the name string (e.g., "AB_3_9.6.2021") into its parts.
    Returns a dict with operator_initials, internal_id, month, day, and year.
    """
    try:
        parts = name_text.split('_')
        operator_initials = parts[0]
        internal_id = int(parts[1])
        # Expecting the date to be in the format month.day.year (e.g., "9.6.2021")
        date_parts = parts[2].split('.')
        if len(date_parts) != 3:
            print(f"Issue parsing name '{name_text}': Date portion does not have three parts. Returning the whole thing for the month, day and year for manual fixing.")
            month, day, year = name_text, name_text, name_text
        else:
            # Convert month, day, year to integers
            month, day, year = map(int, date_parts)
            # Check if year is 2 or 4 digits
            if len(str(year)) != 4:
                if len(str(year)) == 2:
                    print(f"Warning: internal_id {internal_id}; Year '{year}' is only two digits. Adding '20' prefix.")
                    year += 2000
                else:
                    print(f"Warning: internal_id {internal_id}; Year '{year}' is not 2 or four digits. Please manually fix")
        return {
            "operator_initials": operator_initials,
            "internal_id": internal_id,
            "month": month,
            "day": day,
            "year": year
        }
    except Exception as e:
        raise ValueError(f"Error parsing name '{name_text}': {e}. Name properties not returned.")

def parse_description(desc_text): # Note you will need to update to handle special classes (agroforestry etc.)
    """
    Parse the description text into certainty and uncertainty_explanation.
    Expects the first line to be certainty (default to 5 if empty)
    and the second line to be uncertainty_explanation.
    """
    # Split lines and remove empty lines
    lines = [line.strip().lower() for line in desc_text.strip().splitlines() if line.strip()]

    # If there is nothing in the description, assume certainty 5
    if not lines:
        return {"certainty": 5, "uncertainty_explanation": ""}
    
    # If the first line is not an integer, assume certainty 5
    try:
        certainty = int(lines[0]) if lines[0] else 5
    except ValueError:
        # If conversion fails, default to 5
        certainty = 5

    # Add the certainty explanation. If it is absent, set to empty string.
    # Start by assuming the explanation is on the second line
    explanation = lines[1] if len(lines) > 1 else "" 
    # If this line was actually special classes try the third line
    plantation_flags = ["agroforestry", "plantation"]
    commercial_flags = ["commercial", "commercial irrigation"]
    if any(flag in explanation for flag in plantation_flags + commercial_flags):
        explanation = lines[2] if len(lines) > 2 else ""

    # Check for special classes on any line
    plantation = 1 if any(plantation_flag in lines for plantation_flag in plantation_flags) else 0
    commercial = 1 if any(commercial_flag in lines for commercial_flag in commercial_flags) else 0

    return {"certainty": certainty, "uncertainty_explanation": explanation, "plantation": plantation, "commercial": commercial}

def get_color_for_placemark(placemark, root):
    """
    Extracts the color associated with a given KML Placemark element.
    This function navigates through the KML structure to find the color
    defined in the corresponding Style or StyleMap for the provided Placemark.
    It first resolves the styleUrl of the Placemark, then looks up the
    associated StyleMap or Style element, and finally retrieves the color
    from either the LineStyle or PolyStyle.
    Args:
        placemark (xml.etree.ElementTree.Element): The Placemark element from which
            the color is to be extracted.
        root (xml.etree.ElementTree.Element): The root element of the KML document,
            used to search for StyleMap and Style elements.
    Returns:
        str or None: The color value as a string (in KML color format, e.g., "ff0000ff"),
        or None if no color is found.
    """

    # Get the styleUrl from the Placemark
    styleUrl_elem = placemark.find("kml:styleUrl", ns)
    if styleUrl_elem is None or not styleUrl_elem.text:
        return None
    style_id = styleUrl_elem.text.strip().lstrip('#')
    
    # Find the StyleMap element with the corresponding id
    styleMap = root.find(".//kml:StyleMap[@id='" + style_id + "']", ns)
    if styleMap is not None:
        # Look for the <Pair> with key 'normal'
        pair = styleMap.find("kml:Pair[kml:key='normal']", ns)
        if pair is not None:
            normal_styleUrl_elem = pair.find("kml:styleUrl", ns)
            if normal_styleUrl_elem is not None and normal_styleUrl_elem.text:
                normal_style_id = normal_styleUrl_elem.text.strip().lstrip('#')
                # Find the actual Style element with this id
                style_elem = root.find(".//kml:Style[@id='" + normal_style_id + "']", ns)
                if style_elem is not None:
                    # Try to get the color from the LineStyle first; if not available, try PolyStyle
                    color_elem = style_elem.find("kml:LineStyle/kml:color", ns)
                    if color_elem is None or not color_elem.text:
                        color_elem = style_elem.find("kml:PolyStyle/kml:color", ns)
                    if color_elem is not None and color_elem.text:
                        return color_elem.text.strip()
    return None

def convert_color_to_im_num(color):
    """
    Converts a hexadecimal color code from the format 'aabbggrr' to 'bbggrr' 
    and maps it to a corresponding integer identifier representing which number image is being mapped.
    Parameters:
    color (str): A hexadecimal color code in the format 'aabbggrr'.
    Returns:
    int: The integer identifier corresponding to the color if it matches 
         one of the predefined colors in the mapping.
    None: If the color does not match any of the predefined colors.
    Notes:
    - The function assumes the input color is in the format 'aabbggrr' 
      and strips the first two characters to convert it to 'bbggrr'.
    - If the color is not found in the predefined mapping, a message is 
      printed, and the function returns None.
    """

    # turn color from aabbggrr to bbggrr
    color = color[2:]

    color_convert = {1: 'ffffff', 
                     2: '0affff', 
                     3: '0701fc',
                     4: '800080', 
                     5: '0880fd', 
                     6: 'ff02fc', 
                     7: '06ff21', 
                     8: 'ffff20', 
                     9: '336699', 
                     10: 'ff0000'}
    
    if color in color_convert.values():
        return list(color_convert.keys())[list(color_convert.values()).index(color)]
    else:
        # print("Warning: Not one of the main colors used. Returning None for the color value.")
        return None

def convert_geometry(placemark):
    """
    Converts a KML geometry element (Point, LineString, or Polygon) to a GeoJSON geometry dict.
    """
    # Check for Point
    point = placemark.find("kml:Point", ns)
    if point is not None:
        print ("Warning: Point found in kml. Passing over and not converting to GeoJSON")
        return None
    
    # Check for LineString
    linestring = placemark.find("kml:LineString", ns)
    if linestring is not None:
        print ("Warning: LineString found in kml. Passing over and not converting to GeoJSON")
        return None

    # Check for Polygon (only handling the outer boundary)
    polygon = placemark.find("kml:Polygon", ns)
    if polygon is not None:
        outer = polygon.find("kml:outerBoundaryIs/kml:LinearRing", ns)
        if outer is None:
            raise ValueError("Polygon without an outerBoundaryIs/LinearRing element")
        coords_text = outer.find("kml:coordinates", ns).text.strip()
        coords = []
        for coord in coords_text.split():
            parts = coord.split(',')
            lon, lat = float(parts[0]), float(parts[1])
            coords.append([lon, lat])
        # GeoJSON expects polygons as a list of linear rings.
        return {"type": "Polygon", "coordinates": [coords]}
    
    # If no supported geometry is found, return None.
    return None

def kml_to_geojson(kml_file):
    """
    Converts a KML file that contains a folder of polygons exported from Google 
    Earth Pro to a GeoJSON file and returns a GeoPandas GeoDataFrame.
    This function parses a KML file, extracts placemark data, converts the geometries 
    to GeoJSON format, and writes the resulting GeoJSON to a file. It also returns 
    a GeoPandas GeoDataFrame created from the GeoJSON features.
    Args:
        kml_file (str): The file path to the input KML file.
    Returns:
        geopandas.GeoDataFrame: A GeoDataFrame containing the features from the 
        converted GeoJSON file.
    Notes:
        - The function expects the KML file to have placemarks with <name>, 
          <description>, and geometry elements.
        - The <name> element is parsed to extract properties using the `parse_name` function.
        - The <description> element is parsed to extract additional properties using 
          the `parse_description` function.
        - The color of the placemark is extracted and converted to an image number 
          using `get_color_for_placemark` and `convert_color_to_im_num`.
        - If a placemark lacks a supported geometry, it is skipped.
        - The resulting GeoJSON file is saved in the same directory as the input KML file, 
          with the same name but a `.geojson` extension.
    Raises:
        ValueError: If the <name> element cannot be parsed by `parse_name`.
    Example:
        >>> gdf = kml_to_geojson("example.kml")
        GeoJSON written to example.geojson
        >>> print(gdf.head())
    """
    

    tree = ET.parse(kml_file)
    root = tree.getroot()

    features = []

    # Iterate over each Placemark in the KML
    for placemark in root.findall(".//kml:Placemark", ns):
        # Extract and parse <name>
        name_elem = placemark.find("kml:name", ns)
        if name_elem is None or not name_elem.text:
            continue  # Skip placemarks without a name
        try:
            props = parse_name(name_elem.text.strip())
        except ValueError as e:
            print(e)
            props = {}

        # Extract and parse <description>
        desc_elem = placemark.find("kml:description", ns)
        if desc_elem is not None and desc_elem.text:
            desc_props = parse_description(desc_elem.text)
        else:
            desc_props = {"certainty": 5, "uncertainty_explanation": ""}

        # Extract and convert color to image number
        color = get_color_for_placemark(placemark, root)
        if color is not None:
            color_im_num = convert_color_to_im_num(color)
        else: 
            color_im_num = None
        color_props = {"color": color,"color_im_num": color_im_num}

        # Merge properties
        properties = {"name": name_elem.text, **props, **desc_props, **color_props}

        # Convert the geometry
        geometry = convert_geometry(placemark)
        if geometry is None:
            print(f"No supported geometry found for placemark {name_elem.text}")
            continue

        # Build a GeoJSON feature
        feature = {
            "type": "Feature",
            "properties": properties,
            "geometry": geometry
        }
        features.append(feature)

    # Build the FeatureCollection
    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }

    # Write the GeoJSON to a file
    processed_folder = os.path.dirname(kml_file).replace("/raw/", "/processed/")
    os.makedirs(processed_folder, exist_ok=True)
    geojson_file = os.path.join(processed_folder, os.path.basename(kml_file).replace(".kml", ".geojson"))

    with open(geojson_file, "w") as f:
        json.dump(feature_collection, f, indent=2)
    print(f"GeoJSON written to {geojson_file}")

    gdf = gpd.GeoDataFrame.from_features(feature_collection["features"])
    return gdf

# Example usage:
if __name__ == "__main__":

    # Example usage/test code

    # kml = "data/labels/labeled_surveys/random_sample/raw/AB_JL_101-125.kml"
    # gdf = kml_to_geojson(kml)
    # print(gdf.head)

    import argparse

    parser = argparse.ArgumentParser(description="Convert KML to GeoJSON.")
    parser.add_argument("kml_file", type=str, help="Path to the KML file to convert.")
    args = parser.parse_args()
    
    kml_file = args.kml_file
    gdf = kml_to_geojson(kml_file)
    
    print(f"GeoJSON written to {os.path.splitext(kml_file)[0]}.geojson")
