# src/image_to_stitch_preview.py

import numpy as np
from PIL import Image
import yaml
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import cv2

# ---------------------------
# Load yarn palette
# ---------------------------
def load_yarn_palette(yaml_file: Path):
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)
    return {name: hex_code for name, hex_code in data["colours"].items()}

# ---------------------------
# Map pixel colour to nearest yarn colour
# ---------------------------
def nearest_colour(rgb, yarn_palette):
    r, g, b = map(int, rgb)
    min_dist = float("inf")
    closest = None
    for name, hex_code in yarn_palette.items():
        yr, yg, yb = tuple(int(hex_code.lstrip("#")[i:i+2], 16) for i in (0,2,4))
        dist = (r - yr)**2 + (g - yg)**2 + (b - yb)**2
        if dist < min_dist:
            min_dist = dist
            closest = name
    return closest

# ---------------------------
# Determine stitch type using edges and brightness
# ---------------------------
def edge_brightness_to_stitch(pixel_rgb, edge_strength):
    r, g, b = pixel_rgb
    brightness = 0.299*r + 0.587*g + 0.114*b
    if edge_strength > 150:  # strong edges only
        return 'x'
    elif brightness < 100:
        return '+'
    else:
        return 'o'

# ---------------------------
# Resize image to stitch grid
# ---------------------------
def image_to_grid(image_path: str, rows: int, cols: int):
    img = Image.open(image_path).convert("RGB")
    img_small = img.resize((cols, rows), Image.NEAREST)
    return np.array(img_small)

# ---------------------------
# Compute edge map
# ---------------------------
def compute_edge_strength(image_path: str, rows: int, cols: int):
    img = cv2.imread(str(image_path))
    img_small = cv2.resize(img, (cols, rows), interpolation=cv2.INTER_NEAREST)
    gray = cv2.cvtColor(img_small, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)  # stronger thresholds
    return edges

# ---------------------------
# Build stitch + colour grid
# ---------------------------
def image_to_stitch_preview(image_path: str, yarn_palette: dict, rows: int, cols: int):
    grid = image_to_grid(image_path, rows, cols)
    edges = compute_edge_strength(image_path, rows, cols)

    stitch_grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            pixel_rgb = tuple(grid[r, c])
            colour_name = nearest_colour(pixel_rgb, yarn_palette)
            stitch_symbol = edge_brightness_to_stitch(pixel_rgb, edges[r, c])
            row.append((stitch_symbol, colour_name))
        stitch_grid.append(row)
    return stitch_grid

# ---------------------------
# Visualize stitch + colour grid alongside original
# ---------------------------
def visualize_stitch_preview(stitch_grid, yarn_palette, image_path):
    rows, cols = len(stitch_grid), len(stitch_grid[0])
    fig, axes = plt.subplots(1, 2, figsize=(cols/2*2, rows/2))

    # Original image
    img = Image.open(image_path).convert("RGB")
    axes[0].imshow(img)
    axes[0].set_title("Original Image")
    axes[0].axis("off")

    # Stitch preview
    ax = axes[1]
    ax.set_xlim(-0.5, cols-0.5)
    ax.set_ylim(-0.5, rows-0.5)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.axis("off")
    fontsize = max(6, 500 // max(rows, cols))

    for r in range(rows):
        for c in range(cols):
            stitch_symbol, colour_name = stitch_grid[r][c]
            hex_code = yarn_palette[colour_name]
            ax.text(c, r, stitch_symbol, color=hex_code,
                    ha="center", va="center", fontsize=fontsize, fontweight="bold")

    # Legend outside top-right
    legend_elements = [
        mpatches.Patch(color='black', label='o = flat/light area'),
        mpatches.Patch(color='black', label='+ = medium/shaded area'),
        mpatches.Patch(color='black', label='x = edge/contour')
    ]
    ax.legend(
        handles=legend_elements,
        loc='upper left',
        bbox_to_anchor=(1.05, 1),
        fontsize=10,
        framealpha=1,
        facecolor='lightgrey'
    )

    ax.set_title("Stitch + Colour Preview")
    plt.tight_layout()
    plt.show()

# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    ROOT = Path(__file__).resolve().parent.parent
    yarn_file = ROOT / "yarn_palette.yaml"
    yarn_palette = load_yarn_palette(yarn_file)

    image_path = ROOT / "test.png"
    print(f"Using image: {image_path}")

    # Smart grid sizing
    cols = int(input("Number of columns (stitches): "))
    img = Image.open(image_path)
    aspect_ratio = img.height / img.width
    rows = int(cols * aspect_ratio)
    print(f"Automatic rows calculated to preserve aspect ratio: {rows}")

    stitch_width_cm = float(input("Width of one stitch (cm): "))
    stitch_height_cm = float(input("Height of one stitch (cm): "))

    stitch_grid = image_to_stitch_preview(str(image_path), yarn_palette, rows, cols)

    # Pattern dimensions
    pattern_width = cols * stitch_width_cm
    pattern_height = rows * stitch_height_cm
    print(f"\nEstimated pattern dimensions: {pattern_width:.1f} cm × {pattern_height:.1f} cm")

    # Print grid in terminal
    print("\nStitch + Colour grid:")
    for row in stitch_grid:
        print(" ".join(f"{s[0]}({s[1]})" for s in row))

    # Visualize
    visualize_stitch_preview(stitch_grid, yarn_palette, image_path)
