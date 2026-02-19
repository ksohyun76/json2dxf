import ezdxf
import json
import sys
import os

# Meter to millimeter conversion scale
SCALE = 1000

def load_config():
    """
    Load layer configuration from external JSON file.
    The path is relative to the execution directory.
    """
    # Look for config.json inside the rect-box folder
    config_path = os.path.join('rect-box', 'config.json')
    
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found.")
        print(f"Current Directory: {os.getcwd()}")
        sys.exit(1)
        
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_dxf_from_json(input_json_path, output_dxf_path):
    
    config = load_config()
    
    """Read JSON file and convert to DXF file"""
    
    # Read JSON file
    try:
        with open(input_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Cannot find file '{input_json_path}'.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: '{input_json_path}' is not a valid JSON file.")
        sys.exit(1)
    
    # Create new DXF document (AutoCAD 2013 format)
    doc = ezdxf.new('R2013')
    msp = doc.modelspace()
    
    # Collect all types used in JSON data
    used_types = set(item['type'].lower() for item in data)
    
    # Calculate floor bounds from wall objects
    wall_objects = [item for item in data if item['type'].lower() == 'wall']
    floor_bounds = None
    
    if wall_objects:
        # Find the bounding box of all walls
        min_x = min(item['position']['x'] * SCALE for item in wall_objects)
        min_y = min(item['position']['y'] * SCALE for item in wall_objects)
        
        
        def _wh(item):
            w = item['dimensions']['width']
            h = item['dimensions']['height']
            if str(item.get('orientation','')).lower() == 'vertical':
                w, h = h, w
            return w, h
        
        max_x = max((item['position']['x'] + _wh(item)[0]) * SCALE for item in wall_objects)
        max_y = max((item['position']['y'] + _wh(item)[1]) * SCALE for item in wall_objects)
        
        #max_x = max((item['position']['x'] + item['dimensions']['width']) * SCALE for item in wall_objects)
        #max_y = max((item['position']['y'] + item['dimensions']['height']) * SCALE for item in wall_objects)
        
        floor_bounds = {
            'min_x': min_x,
            'min_y': min_y,
            'max_x': max_x,
            'max_y': max_y
        }
        
        # Add 'floor' to used types if walls exist
        used_types.add('floor')
        print(f"Floor bounds calculated from walls: ({min_x:.0f}, {min_y:.0f}) to ({max_x:.0f}, {max_y:.0f})")
    
    # Create layers (only for used types) with True Color
    for item_type in used_types:
        layer_name = item_type.upper()
        #rgb_color = LAYER_COLORS.get(item_type, DEFAULT_COLOR)
        layer_info = config['layers'].get(layer_name, config['defaults'])
        rgb_color = int(layer_info['color'],16) # type : hex
        
        # Create layer
        layer = doc.layers.add(layer_name)
        
        # Set True Color (RGB) - ezdxf handles the conversion
        layer.color = -1  # Indicates True Color usage in AutoCAD
        layer.rgb = (
            (rgb_color >> 16) & 0xFF,  # Red
            (rgb_color >> 8) & 0xFF,   # Green
            rgb_color & 0xFF           # Blue
        )
        
        print(f"Layer created: {layer_name} (RGB: #{rgb_color:06X})")
    
    # Create floor polyline if walls exist (2D LWPOLYLINE for solid fill)
    if floor_bounds:
        floor_points = [
            (floor_bounds['min_x'], floor_bounds['min_y']),
            (floor_bounds['max_x'], floor_bounds['min_y']),
            (floor_bounds['max_x'], floor_bounds['max_y']),
            (floor_bounds['min_x'], floor_bounds['max_y']),
            (floor_bounds['min_x'], floor_bounds['min_y'])  # Close the polyline
        ]
        
        # Use LWPOLYLINE for floor (2D, can be filled)
        msp.add_lwpolyline(floor_points, dxfattribs={'layer': 'FLOOR'})
        print(f"Floor entity created on FLOOR layer (2D LWPOLYLINE at z=0)")
    
    # Iterate through JSON data and create drawing entities
    for item in data:
        item_type = item['type'].upper()
        #item_type_lower = item['type'].lower()
        x = item['position']['x'] * SCALE
        y = item['position']['y'] * SCALE
        width = item['dimensions']['width'] * SCALE
        height = item['dimensions']['height'] * SCALE
        
        # Apply orientation (vertical/horizontal) to geometry
        # If orientation is 'vertical', swap width/height to reflect 90° rotation in DXF
        orientation = str(item.get('orientation', '')).lower()
        if orientation == 'vertical':
            width, height = height, width
        
        # Get Z coordinate (height) for this layer type
        #z_coord = LAYER_HEIGHTS.get(item_type_lower, DEFAULT_HEIGHT)
        height_info = config['layers'].get(item_type, config['defaults'])
        z_coord = height_info['height']
        
        
        points = [
            (x, y, z_coord),
            (x + width, y, z_coord),
            (x + width, y + height, z_coord),
            (x, y + height, z_coord),
            (x, y, z_coord)  # Repeat start point for closed polyline
        ]
        
        # Add 3D polyline to appropriate layer
        msp.add_polyline3d(points, dxfattribs={'layer': item_type})
        
    print(f"\nHeight mapping used:")
    for layer_type in used_types:
        if layer_type != 'floor':
            #z = LAYER_HEIGHTS.get(layer_type, DEFAULT_HEIGHT)
            layer_name = layer_type.upper()
            h_info = config['layers'].get(layer_name, config['defaults'])
            z = h_info['height']
            print(f"  {layer_type.upper()}: z={z}mm")
    
    # Save file
    try:
        doc.saveas(output_dxf_path)
        print(f"\n✓ DXF file created: {output_dxf_path}")
        print(f"✓ Total entities: {len(data)}")
        if floor_bounds:
            print(f"✓ Floor layer added automatically")
    except Exception as e:
        print(f"Error: Failed to save DXF file - {e}")
        sys.exit(1)


def print_usage():
    """Print usage instructions"""
    print("Usage: python json2dxf.py <input_JSON_file> <output_DXF_file>")


def main():
    # Check command line arguments
    if len(sys.argv) != 3:
        print("Error: Incorrect number of arguments.\n")
        print_usage()
        sys.exit(1)
    
    input_json = sys.argv[1]
    output_dxf = sys.argv[2]
    
    print(f"Input JSON: {input_json}")
    print(f"Output DXF: {output_dxf}")
    print("-" * 50)
    
    create_dxf_from_json(input_json, output_dxf)


if __name__ == "__main__":
    main()