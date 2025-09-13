# src/image_to_pattern_vectorised.py

from pathlib import Path
from PIL import Image
import polars as pl
import numpy as np
import yaml
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ---------------------------
# Load yarn palette
# ---------------------------
def load_yarn_palette(yaml_file: Path):
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)
    return {name.lower(): hex_code for name, hex_code in data["colours"].items()}

# ---------------------------
# Vectorised resizing using nearest neighbor
# ---------------------------
def resize_image(img_array, new_rows, new_cols):
    old_rows, old_cols, _ = img_array.shape
    row_idx = (np.arange(new_rows) * (old_rows / new_rows)).astype(int)
    col_idx = (np.arange(new_cols) * (old_cols / new_cols)).astype(int)
    resized = img_array[row_idx[:, None], col_idx]
    return resized

# ---------------------------
# Vectorised Sobel edge detection
# ---------------------------
def compute_edges(img_array):
    gray = 0.299 * img_array[:, :, 0] + 0.587 * img_array[:, :, 1] + 0.114 * img_array[:, :, 2]
    gray = gray.astype(float)

    Kx = np.array([[-1,0,1],[-2,0,2],[-1,0,1]], dtype=float)
    Ky = np.array([[1,2,1],[0,0,0],[-1,-2,-1]], dtype=float)

    gray_padded = np.pad(gray, ((1,1),(1,1)), mode='edge')

    gx = (Kx[0,0]*gray_padded[:-2,:-2] + Kx[0,1]*gray_padded[:-2,1:-1] + Kx[0,2]*gray_padded[:-2,2:] +
          Kx[1,0]*gray_padded[1:-1,:-2] + Kx[1,1]*gray_padded[1:-1,1:-1] + Kx[1,2]*gray_padded[1:-1,2:] +
          Kx[2,0]*gray_padded[2:,:-2] + Kx[2,1]*gray_padded[2:,1:-1] + Kx[2,2]*gray_padded[2:,2:])

    gy = (Ky[0,0]*gray_padded[:-2,:-2] + Ky[0,1]*gray_padded[:-2,1:-1] + Ky[0,2]*gray_padded[:-2,2:] +
          Ky[1,0]*gray_padded[1:-1,:-2] + Ky[1,1]*gray_padded[1:-1,1:-1] + Ky[1,2]*gray_padded[1:-1,2:] +
          Ky[2,0]*gray_padded[2:,:-2] + Ky[2,1]*gray_padded[2:,1:-1] + Ky[2,2]*gray_padded[2:,2:])

    return np.sqrt(gx**2 + gy**2)

# ---------------------------
# Vectorised nearest colour mapping
# ---------------------------
def nearest_colour_vectorised(img_array, yarn_palette):
    palette_names = list(yarn_palette.keys())
    palette_rgb = np.array([[int(hex_code.lstrip('#')[i:i+2],16) for i in (0,2,4)]
                            for hex_code in yarn_palette.values()])
    flat_img = img_array.reshape(-1,3)
    dist = np.sum((flat_img[:,None,:] - palette_rgb[None,:,:])**2, axis=2)
    idx = np.argmin(dist, axis=1)
    nearest_names = [palette_names[i] for i in idx]
    return np.array(nearest_names).reshape(img_array.shape[:2])

# ---------------------------
# Assign stitch type
# ---------------------------
def edge_brightness_to_stitch_vectorised(img_array, edge_array):
    brightness = 0.299*img_array[:,:,0] + 0.587*img_array[:,:,1] + 0.114*img_array[:,:,2]
    stitches = np.full(brightness.shape, 'o', dtype='<U1')
    stitches[brightness<100] = '+'
    stitches[edge_array>150] = 'x'
    return stitches

# ---------------------------
# Build stitch grid using Polars
# ---------------------------
def image_to_stitch_grid(img_array, edge_array, yarn_palette):
    colour_array = nearest_colour_vectorised(img_array, yarn_palette)
    stitch_array = edge_brightness_to_stitch_vectorised(img_array, edge_array)

    rows, cols = img_array.shape[:2]
    data = [(r,c,stitch_array[r,c],colour_array[r,c]) for r in range(rows) for c in range(cols)]
    df = pl.DataFrame(data, schema=["row","col","stitch","colour"], orient="row")
    return df

# ---------------------------
# Visualise stitch grid (save or show)
# ---------------------------
def visualise_stitch_grid(df, yarn_palette, rows, cols, image_path, output_path=None):
    fig, axes = plt.subplots(1,2, figsize=(cols/2*2, rows/2))

    img = Image.open(image_path).convert("RGB")
    axes[0].imshow(img)
    axes[0].set_title("Original Image")
    axes[0].axis("off")

    ax = axes[1]
    ax.set_xlim(-0.5, cols-0.5)
    ax.set_ylim(-0.5, rows-0.5)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.axis("off")
    fontsize = max(6, 500//max(rows, cols))

    for r,c,stitch,colour_name in df.select(["row","col","stitch","colour"]).to_numpy():
        r = int(r); c = int(c)
        colour_name = str(colour_name).strip().lower()
        hex_code = yarn_palette.get(colour_name,"#000000")
        ax.text(c,r,stitch,color=hex_code,ha="center",va="center",
                fontsize=fontsize,fontweight="bold")

    legend_elements = [
        mpatches.Patch(color='black', label='o = flat/light area'),
        mpatches.Patch(color='black', label='+ = medium/shaded area'),
        mpatches.Patch(color='black', label='x = edge/contour')
    ]
    legend = ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.05,1),
                       fontsize=10, framealpha=1, facecolor='lightgrey')
    legend.set_draggable(True)
    ax.set_title("Legend")
    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150)
        plt.close(fig)
    else:
        plt.show()

# ---------------------------
# Main (CLI)
# ---------------------------
if __name__=="__main__":
    ROOT = Path(__file__).resolve().parent.parent
    yarn_file = ROOT/"yarn_palette.yaml"
    yarn_palette = load_yarn_palette(yarn_file)

    image_path = ROOT/"test.png"
    img = np.array(Image.open(image_path).convert("RGB"))

    cols = int(input("Number of columns (stitches): "))
    aspect_ratio = img.shape[0]/img.shape[1]
    rows = int(cols*aspect_ratio)

    stitch_width_cm = float(input("Width of one stitch (cm): "))
    stitch_height_cm = float(input("Height of one stitch (cm): "))

    resized_img = resize_image(img, rows, cols)
    edges = compute_edges(resized_img)
    stitch_df = image_to_stitch_grid(resized_img, edges, yarn_palette)

    pattern_width = cols*stitch_width_cm
    pattern_height = rows*stitch_height_cm
    print(f"\nEstimated pattern dimensions: {pattern_width:.1f} cm × {pattern_height:.1f} cm")

    print("\nStitch + Colour grid:")
    for r in range(rows):
        row_data = stitch_df.filter(pl.col("row")==r).sort("col")
        print(" ".join(f"{s[2]}({s[3]})" for s in row_data.iter_rows()))

    visualise_stitch_grid(stitch_df, yarn_palette, rows, cols, image_path)


