
---

# iCrochet

iCrochet is a Python project that converts an image into a crochet pattern preview. It maps pixels to the nearest yarn colours and estimates stitch types based on image brightness and edge detection. The user can visualise the resulting stitch pattern alongside the original image.

This repository contains two main approaches:

1. **Package-driven version** (faster, uses OpenCV/PIL/Matplotlib)
2. **Pure Python/Polars/NumPy version** (manual computation of resising, edges, and color matching)

---

## Features

* Converts an image into a stitch-by-stitch crochet preview
* Maps pixels to the nearest yarn colours from a YAML palette
* Assigns stitches based on brightness and edge detection:

  * `o` = flat/light area
  * `+` = medium/shaded area
  * `x` = edge/contour
* Estimates pattern dimensions based on user-provided stitch sise
* Side-by-side visualisation of original image and stitch preview
* Customisable yarn palette via YAML
* Terminal output of stitch grid

---

## Installation

```bash
git clone <repo_url>
cd iCrochet
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

**Requirements** (for package-driven version):

* Python 3.10+
* numpy
* polars
* pillow
* matplotlib
* pyyaml

---

## Usage

```bash
python src/image_to_stitch.py
```

**User Input Prompts:**

1. Number of columns (stitches)
2. Width of one stitch (cm)
3. Height of one stitch (cm)

**Output:**

* Terminal: stitch grid with stitch type and colour
* Matplotlib figure: original image + stitch-colored preview
* Estimated pattern dimensions (cm)

---

## Yarn Palette

Example `yarn_palette.yaml`:

```yaml
colours:
  red: "#FF0000"
  blue: "#0000FF"
  green: "#00FF00"
  yellow: "#FFD700"
  brown: "#8B4513"
  black: "#000000"
```

Users can add their own yarn colours to this file.

---

## Version 1: Package-driven (OpenCV/PIL, built-in edge detection)

**How it works:**

1. **Resising**: Uses PIL’s `resise` method for quick downsampling.
2. **Edge detection**: Uses either OpenCV or NumPy-based Sobel filtering.
3. **Colour mapping**: For each pixel, calculates Euclidean distance in RGB space to all yarn colours in the palette and picks the closest.
4. **Stitch assignment**:

   * Bright areas → `o`
   * Medium areas → `+`
   * Strong edges → `x`
5. **Visualisation**: Matplotlib plots the original and stitch preview, with stitch types colored according to yarn.

This version is **faster and more accurate**, especially for large images.

---

## Version 2: Pure Python / Polars / NumPy

This version avoids external CV libraries for core computations, implementing everything manually. It uses:

* **Nearest-neighbour resising**: Manually maps new pixel coordinates to original image pixels.
* **Sobel filter convolution**: Edge magnitude calculated by manually convolving Sobel kernels with the grayscale image.
* **Manual colour matching**: Loops over each pixel and computes Euclidean distance to each yarn colour.
* **Polars DataFrame**: Stores stitch grid with `row`, `col`, `stitch`, `colour`.
* **Matplotlib visualisation**: Similar side-by-side figure, legend for stitch types.

**Mathematics details:**

* **Brightness (grayscale)**:
  $\text{brightness} = 0.299 R + 0.587 G + 0.114 B$
* **Edge magnitude (Sobel filter)**:
  $G_x = K_x * I, \quad G_y = K_y * I$
  $\text{edge} = \sqrt{G_x^2 + G_y^2}$
* **Nearest yarn colour**:
  For each pixel `(r,g,b)`, find the palette colour `(R_i, G_i, B_i)` that minimises:
  $\text{distance}^2 = (r-R_i)^2 + (g-G_i)^2 + (b-B_i)^2$
* **Stitch type assignment**:

  * Edge > 150 → `x`
  * Brightness < 100 → `+`
  * Else → `o`
* **Pattern dimension estimation**:
  $\text{width} = \text{columns} \times \text{stitch\_width\_cm}$
  $\text{height} = \text{rows} \times \text{stitch\_height\_cm}$

This version is **slower but educational**, demonstrating the mathematics behind resising, edge detection, and colour matching.

---

## Customisation

* **Change yarn palette**: Edit `yarn_palette.yaml`.
* **Change stitch types**: Modify `edge_brightness_to_stitch()` thresholds.
* **Adjust grid sise**: User input for columns; rows are scaled automatically by aspect ratio.
* **Change visualisation style**: Font sise, figure sise, and colours can be customised in `visualise_stitch_grid()`.

---

## Example

Terminal output:

```
Number of columns (stitches): 10
Width of one stitch (cm): 1.0
Height of one stitch (cm): 1.0

Estimated pattern dimensions: 10.0 cm × 8.0 cm

Stitch + Colour grid:
o(red) +(blue) o(green) x(yellow) ...
...
```

Matplotlib figure:

* Left: original image
* Right: stitch preview, each stitch coloured according to the palette, with `o`, `+`, `x` symbols and a legend.

---

## License

MIT License by default. Can be changed to a more restrictive license for commercial use.

---

