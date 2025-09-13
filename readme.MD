
---

# iCrochet

iCrochet is a Python project that converts an image into a crochet pattern preview. It maps pixels to the nearest yarn colours and estimates stitch types based on image brightness and edge detection. The user can visualise the resulting stitch pattern alongside the original image.

This repository contains two main approaches:

1. **Package-driven version** (faster, uses OpenCV/PIL/Matplotlib)
2. **Pure Python/Polars/NumPy version** (manual computation of resizing, edges, and color matching)

---

## Features

* Converts an image into a stitch-by-stitch crochet preview
* Maps pixels to the nearest yarn colours from a YAML palette
* Assigns stitches based on brightness and edge detection:

```
'o' = flat/light area
'+' = medium/shaded area
'x' = edge/contour
```

* Estimates pattern dimensions based on user-provided stitch size
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

1. **Resizing**: Uses PIL’s `resize` method for quick downsampling.
2. **Edge detection**: Uses either OpenCV or NumPy-based Sobel filtering.
3. **Colour mapping**: For each pixel, calculates Euclidean distance in RGB space to all yarn colours in the palette and picks the closest.
4. **Stitch assignment**:

```
Bright areas → 'o'
Medium areas → '+'
Strong edges → 'x'
```

5. **Visualisation**: Matplotlib plots the original and stitch preview, with stitch types colored according to yarn.

This version is **faster and more accurate**, especially for large images.

---

## Version 2: Pure Python / Polars / NumPy

This version avoids external CV libraries for core computations, implementing everything manually. It uses:

* **Nearest-neighbour resizing**: Manually maps new pixel coordinates to original image pixels.
* **Sobel filter convolution**: Edge magnitude calculated by manually convolving Sobel kernels with the grayscale image.
* **Manual colour matching**: Loops over each pixel and computes Euclidean distance to each yarn colour.
* **Polars DataFrame**: Stores stitch grid with `row`, `col`, `stitch`, `colour`.
* **Matplotlib visualisation**: Similar side-by-side figure, legend for stitch types.

**Mathematics details:**

**Brightness (grayscale):**

```
brightness = 0.299 * R + 0.587 * G + 0.114 * B
```

**Edge magnitude (Sobel filter):**

```
Gx = Kx * I
Gy = Ky * I
edge = sqrt(Gx^2 + Gy^2)
```

**Nearest yarn colour:**

```
For each pixel (r,g,b), find the palette colour (Ri, Gi, Bi) that minimises:
distance^2 = (r - Ri)^2 + (g - Gi)^2 + (b - Bi)^2
```

**Stitch type assignment:**

```
if edge > 150: stitch = 'x'
elif brightness < 100: stitch = '+'
else: stitch = 'o'
```

**Pattern dimension estimation:**

```
width  = columns * stitch_width_cm
height = rows    * stitch_height_cm
```

This version is **slower but educational**, demonstrating the mathematics behind resizing, edge detection, and colour matching.

---

## Customisation

* **Change yarn palette**: Edit `yarn_palette.yaml`
* **Change stitch types**: Modify `edge_brightness_to_stitch()` thresholds
* **Adjust grid size**: User input for columns; rows are scaled automatically by aspect ratio
* **Change visualisation style**: Font size, figure size, and colours can be customised in `visualise_stitch_grid()`

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
* Right: stitch preview, each stitch coloured according to the palette, with `o`, `+`, `x` symbols and a legend

---

## Web App

iCrochet also has a **web application** to generate patterns visually:

* Upload an image and convert it into a crochet pattern.
* Specify columns and stitch dimensions.
* Pop-out modal preview of the generated pattern.
* Download the pattern as a **formatted PDF**.

### Technologies

* HTML, CSS, JavaScript
* Google Fonts: [Press Start 2P](https://fonts.google.com/specimen/Press+Start+2P)
* jsPDF for PDF generation
* Python backend (Flask/FastAPI)

### Usage

1. Open `index.html` in a browser.
2. Upload an image.
3. Adjust columns, stitch width, and height.
4. Click **GENERATE**.
5. Preview pattern in modal.
6. Click **DOWNLOAD PDF** to save the formatted crochet pattern.

---

## Demo

If you uploaded your video to `assets/demo_sped.mp4`:

```markdown
[Watch the demo video](assets/demo_sped.mp4)
```

* Clicking the link opens the video in browser.

> For inline autoplay on GitHub, you can also convert the video to a GIF (`demo_sped.gif`) and reference it:

```markdown
![iCrochet Demo](assets/demo_sped.gif)
```

---

## Folder Structure

```
iCrochet/
├── assets/
│   ├── demo_sped.mp4
│   └── demo_sped.gif   # optional
├── index.html
├── README.md
├── src/
│   └── image_to_stitch.py
└── ...
```

---

## Contributing

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Open a Pull Request.

---

## License

MIT License. See `LICENSE` for details.

---


