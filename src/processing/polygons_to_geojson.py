import xml.etree.ElementTree as ET
import json

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
            raise ValueError("Date portion does not have three parts.")
        month, day, year = map(int, date_parts)
        if len(str(year)) != 4:
            print(f"Warning: internal_id {internal_id}; Year {year} does not have four digits. Adding '20' prefix.")
            year += 2000
        return {
            "operator_initials": operator_initials,
            "internal_id": internal_id,
            "month": month,
            "day": day,
            "year": year
        }
    except Exception as e:
        raise ValueError(f"Error parsing name '{name_text}': {e}")

def parse_description(desc_text): # Note you will need to update to handle special classes (agroforestry etc.)
    """
    Parse the description text into certainty and uncertainty_explanation.
    Expects the first line to be certainty (default to 5 if empty)
    and the second line to be uncertainty_explanation.
    """
    # Split lines and remove empty lines
    lines = [line.strip() for line in desc_text.strip().splitlines() if line.strip()]
    if not lines:
        return {"certainty": 5, "uncertainty_explanation": ""}
    try:
        certainty = int(lines[0]) if lines[0] else 5
    except ValueError:
        # If conversion fails, default to 5
        certainty = 5
    explanation = lines[1] if len(lines) > 1 else ""
    return {"certainty": certainty, "uncertainty_explanation": explanation}

def get_color_for_placemark(placemark, root):
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
        print("Not one of the main colors used")
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

def kml_to_geojson(kml_file, geojson_file):
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
            continue

        # Extract and parse <description>
        desc_elem = placemark.find("kml:description", ns)
        if desc_elem is not None and desc_elem.text:
            desc_props = parse_description(desc_elem.text)
        else:
            desc_props = {"certainty": 5, "uncertainty_explanation": ""}

        # Extract and convert color to image number
        color = get_color_for_placemark(placemark, root)
        if color is not None:
            im_num = convert_color_to_im_num(color)
        color_props = {"color": color, "image_number": im_num}

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
    with open(geojson_file, "w") as f:
        json.dump(feature_collection, f, indent=2)
    print(f"GeoJSON written to {geojson_file}")

# Example usage:
if __name__ == "__main__":
    kml_file_path = "data/labels/test/Zambia_0.05_n_1-50.kml"  # update with your actual file path
    geojson_file_path = "data/labels/test/Zambia_0.05_n_1-50.geojson"
    kml_to_geojson(kml_file_path, geojson_file_path)
