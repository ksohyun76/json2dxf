# DXF 3D Viewer - Rectangular Box Rendering

A tool that reads 2D floor plan data from JSON files, converts them to DXF format, and visualizes them in 3D in a web browser.

## 📁 File Structure

```
project-root/           # Project root (create virtual environment here)
├── venv/               # Virtual environment (create once)
└── rect-box/
    ├── config.json          # Layer settings (Colors & Heights)
    ├── json2dxf.py          # JSON → DXF conversion script
    ├── index.html           # DXF 3D Viewer (Web)
    └── test/                # Test files directory
        ├── data_*.json # Sample input JSON file
        └── data_*.dxf  # Generated DXF file
```

## 🚀 Quick Start

### 1. Generate DXF File

```bash
# Create and activate virtual environment at project root (first time only)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate DXF from JSON (run from project root)
python rect-box/json2dxf.py rect-box/test/data_2.json rect-box/test/data_2.dxf
```

### 2. View in 3D Viewer

```bash
# Start web server (from project root directory)
python -m http.server 8000

# Open in browser
# http://localhost:8000/rect-box/index.html?file=/rect-box/test/data_2.dxf
```

## 📝 JSON Input Format

### Basic Structure

The JSON file consists of an array of objects (entities). Each object has the following properties:

```json
[
    {
        "type": "object_type",
        "position": {"x": X_coordinate, "y": Y_coordinate},
        "dimensions": {"width": width, "height": height},
        "orientation": "horizontal or vertical"
    }
]
```

### Property Descriptions

| Property | Type | Description | Example |
|----------|------|-------------|---------|
| `type` | string | Object type (layer name) | `"wall"`, `"door"`, `"shelf"` |
| `position.x` | number | Bottom-left X coordinate (meters) | `0.0`, `3.5` |
| `position.y` | number | Bottom-left Y coordinate (meters) | `0.0`, `1.0` |
| `dimensions.width` | number | Width (meters) | `10.0`, `2.0` |
| `dimensions.height` | number | Height (meters) | `0.2`, `1.5` |
| `orientation` | string | Orientation (for reference) | `"horizontal"`, `"vertical"` |

### Coordinate System

```
Y-axis (North)
  ↑
  │
  │
  └──────→ X-axis (East)
(0,0)
```

- Origin (0,0) is at the bottom-left
- X-axis: increases from left to right
- Y-axis: increases from bottom to top
- Unit: meters (internally converted to millimeters)

### Sample Data

```json
[
    {
        "type": "wall",
        "position": {"x": 0.0, "y": 0.0},
        "dimensions": {"width": 10.0, "height": 0.2},
        "orientation": "horizontal"
    },
    {
        "type": "shelf",
        "position": {"x": 0.5, "y": 1.0},
        "dimensions": {"width": 2.0, "height": 0.3},
        "orientation": "horizontal"
    }
]
```

## 🎨 Object Types (Layers)

### Default Supported Types

**Colors are synchronized between AutoCAD and 3D viewer using RGB True Color**

| Type | Layer Name | Hex Code | Height (mm) | Purpose |
|------|------------|----------|----------|---------|
| `wall` | WALL | `#4A90E2` | 2800 | Walls |
| `shelf` | SHELF | `#F39C12`| 1800 | Shelves |
| `door` | DOOR | `#FFFF00` | 2100 | Doors |
| `chiller` | CHILLER | `#00FFFF` | 2000 | Refrigerators |
| `floor` | FLOOR | `#808080` | 0 | Ground level (auto-generated) |

### Adding New Types

**Step 1: Update config.json**

``` json
{
  "layers": {
    ...
    "DESK": { "color": "0x2ecc71", "height": 750 }
  }
}
```

**Step 3: Use in Input JSON**

```json
{
    "type": "desk",
    "position": {"x": 3.0, "y": 4.0},
    "dimensions": {"width": 1.5, "height": 0.8},
    "orientation": "horizontal"
}
```

## 🔧 json2dxf.py Details

### Command Line Usage

```bash
python rect-box/json2dxf.py <input_JSON_file> <output_DXF_file>
```

**Examples:**
```bash
# Run from project root (with virtual environment activated)
python rect-box/json2dxf.py rect-box/test/data_1.json rect-box/test/data_1.dxf
```

### Key Features

- ✅ JSON file parsing and validation
- ✅ Automatic meters → millimeters conversion (CAD standard)
- ✅ Automatic color assignment by layer
- ✅ Creates layers only for used types (efficient)
- ✅ Error handling with user-friendly messages
- ✅ AutoCAD 2013 format (R2013) compatible


### Output Example

```
Input JSON: rect-box/test/data_1.json
Output DXF: rect-box/test/data_1.dxf
--------------------------------------------------
Floor bounds calculated from walls: (0, 0) to (12000, 8000)
Layer created: WALL (RGB: #4A90E2)
Layer created: FLOOR (RGB: #808080)
Layer created: DOOR (RGB: #FFFF00)
Layer created: SHELF (RGB: #F39C12)
Layer created: CHILLER (RGB: #00FFFF)
Floor entity created on FLOOR layer (2D LWPOLYLINE at z=0)

Height mapping used:
  DOOR: z=2100mm
  SHELF: z=1800mm
  CHILLER: z=2000mm
  WALL: z=2800mm
  
✓ DXF file created: rect-box/test/data_1.dxf
✓ Total entities: 18
✓ Floor layer added automatically
```

## 🌐 index.html Details

### URL Parameters

To change the default filename, use the `?file=` parameter:

```
http://localhost:8000/rect-box/index.html                                   # Load default file
http://localhost:8000/rect-box/index.html?file=/rect-box/test/data_2.dxf    # Load test/data_2.dxf
```

**Note:** File paths use absolute paths starting from the web server root (`/`).

### 3D Rendering Features

- 📦 Renders each rectangle as a 3D box with 2m height
- 🎨 RGB True Color - Same colors as AutoCAD for consistency
- 🌓 Shadow and lighting effects
- 🖱️ Mouse controls (rotation, zoom, pan)
- 📊 Real-time statistics display

### Controls

| Control | Action |
|---------|--------|
| Left-click drag | Rotate camera |
| Mouse wheel | Zoom in/out |
| Right-click drag | Pan camera |


## 📐 Automation Script

```bash
#!/bin/bash
# batch_convert.sh (located at project root)

# Convert all JSON files in rect-box/test/ directory
for json_file in rect-box/test/*.json; do
    dxf_file="${json_file%.json}.dxf"
    echo "Converting $json_file to $dxf_file"
    python rect-box/json2dxf.py "$json_file" "$dxf_file"
done

echo "All files converted!"
```

## 📚 References

- **ezdxf Documentation**: https://ezdxf.readthedocs.io/
- **Three.js Documentation**: https://threejs.org/docs/
- **DXF File Format**: https://images.autodesk.com/adsk/files/autocad_2013_pdf_dxf_reference_enu.pdf 

---

**Last Updated:** 2026
**Version:** 1.0