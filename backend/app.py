# backend/app.py

from flask import Flask, request, jsonify, send_file
from pathlib import Path
from werkzeug.utils import secure_filename
import os
import numpy as np
from src import image_to_pattern_vectorised as ip
import matplotlib
matplotlib.use("Agg")  # non-GUI backend for Flask

from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # allow React requests

# folders
UPLOAD_FOLDER = Path(__file__).parent / "uploads"
OUTPUT_FOLDER = Path(__file__).parent / "outputs"
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

# yarn palette
YARN_FILE = Path(__file__).parent / "yarn_palette.yaml"
yarn_palette = ip.load_yarn_palette(YARN_FILE)

@app.route("/api/upload", methods=["POST"])
def upload_image():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No image uploaded"}), 400

    filename = secure_filename(file.filename)
    filepath = UPLOAD_FOLDER / filename
    file.save(filepath)

    # get parameters
    cols = int(request.form.get("cols", 50))
    stitch_width = float(request.form.get("stitch_width", 1.0))
    stitch_height = float(request.form.get("stitch_height", 1.0))

    # load & resize image
    img = ip.resize_image(np.array(ip.Image.open(filepath).convert("RGB")), cols, cols)
    aspect_ratio = img.shape[0] / img.shape[1]
    rows = int(cols * aspect_ratio)
    resized_img = ip.resize_image(np.array(ip.Image.open(filepath).convert("RGB")), rows, cols)

    # generate stitch pattern
    edges = ip.compute_edges(resized_img)
    stitch_df = ip.image_to_stitch_grid(resized_img, edges, yarn_palette)

    # save output visualization
    output_path = OUTPUT_FOLDER / f"{filename}_pattern.png"
    ip.visualise_stitch_grid(stitch_df, yarn_palette, rows, cols, filepath, output_path=output_path)

    return jsonify({"pattern_image": f"/api/output/{output_path.name}"})


@app.route("/api/output/<filename>")
def serve_output(filename):
    path = OUTPUT_FOLDER / filename
    if path.exists():
        return send_file(path, mimetype="image/png")
    return jsonify({"error": "File not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
