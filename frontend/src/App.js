import React, { useState } from "react";

export default function App() {
  const [image, setImage] = useState(null);
  const [patternURL, setPatternURL] = useState("");
  const [cols, setCols] = useState(50);
  const [stitchWidth, setStitchWidth] = useState(1.0);
  const [stitchHeight, setStitchHeight] = useState(1.0);
  const [isLoading, setIsLoading] = useState(false);
  const [fileName, setFileName] = useState("");

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!image) return;

    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("image", image);
      formData.append("cols", cols);
      formData.append("stitch_width", stitchWidth);
      formData.append("stitch_height", stitchHeight);

      const res = await fetch("http://localhost:5001/api/upload", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setPatternURL(data.pattern_image || "");
    } catch (error) {
      console.error("Upload error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setImage(file);
    setFileName(file ? file.name : "");
  };

  return (
    <div className="min-h-screen bg-gray-900 text-pink-400 flex flex-col items-center px-6 py-8 relative overflow-hidden">
      {/* CRT Scanlines */}
      <div className="scanlines fixed inset-0 pointer-events-none z-50"></div>

      {/* Screen Glow Effect */}
      <div className="screen-glow fixed inset-0 pointer-events-none z-40"></div>

      {/* Main Container */}
      <div className="w-full max-w-4xl mx-auto relative z-10">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl md:text-6xl text-yellow-400 pixel-border inline-block px-8 py-4 mb-4">
            iCrochet
          </h1>
          <p className="text-teal-300 text-sm md:text-base mt-4">
            Transform your images into crochet patterns
          </p>
        </div>

        {/* Upload Form */}
        <div className="bg-black border-4 border-pink-400 p-6 md:p-8 mb-12 relative">
          {/* Corner Decorations */}
          <div className="absolute top-2 left-2 w-4 h-4 border-2 border-yellow-400"></div>
          <div className="absolute top-2 right-2 w-4 h-4 border-2 border-yellow-400"></div>
          <div className="absolute bottom-2 left-2 w-4 h-4 border-2 border-yellow-400"></div>
          <div className="absolute bottom-2 right-2 w-4 h-4 border-2 border-yellow-400"></div>

          <form onSubmit={handleUpload} className="space-y-6">
            {/* File Input */}
            <div className="relative">
              <label className="block text-yellow-300 text-sm mb-3">
                UPLOAD IMAGE
              </label>
              <div className="relative">
                <input
                  type="file"
                  onChange={handleFileChange}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                  accept="image/*"
                />
                <div className="bg-gray-800 border-4 border-teal-400 p-4 text-center cursor-pointer hover:bg-gray-700 transition-colors">
                  {fileName ? (
                    <span className="text-pink-300 text-sm">{fileName}</span>
                  ) : (
                    <span className="text-gray-400">CHOOSE FILE</span>
                  )}
                </div>
              </div>
            </div>

            {/* Options Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Columns */}
              <div className="space-y-2">
                <label className="block text-yellow-300 text-sm">
                  COLUMNS
                </label>
                <input
                  type="number"
                  value={cols}
                  onChange={(e) => setCols(e.target.value)}
                  min="10"
                  max="200"
                  className="w-full bg-gray-800 border-4 border-teal-400 text-pink-300 p-3 text-center focus:border-yellow-400 focus:outline-none"
                />
              </div>

              {/* Stitch Width */}
              <div className="space-y-2">
                <label className="block text-yellow-300 text-sm">
                  WIDTH (CM)
                </label>
                <input
                  type="number"
                  value={stitchWidth}
                  step="0.1"
                  min="0.1"
                  max="5.0"
                  onChange={(e) => setStitchWidth(e.target.value)}
                  className="w-full bg-gray-800 border-4 border-teal-400 text-pink-300 p-3 text-center focus:border-yellow-400 focus:outline-none"
                />
              </div>

              {/* Stitch Height */}
              <div className="space-y-2">
                <label className="block text-yellow-300 text-sm">
                  HEIGHT (CM)
                </label>
                <input
                  type="number"
                  value={stitchHeight}
                  step="0.1"
                  min="0.1"
                  max="5.0"
                  onChange={(e) => setStitchHeight(e.target.value)}
                  className="w-full bg-gray-800 border-4 border-teal-400 text-pink-300 p-3 text-center focus:border-yellow-400 focus:outline-none"
                />
              </div>
            </div>

            {/* Upload Button */}
            <div className="text-center pt-4">
              <button
                type="submit"
                disabled={!image || isLoading}
                className="arcade-button bg-pink-500 text-black border-4 border-yellow-400 px-12 py-4
                         hover:bg-pink-400 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed
                         transition-all duration-150 relative group"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center">
                    <span className="animate-pulse">PROCESSING...</span>
                  </span>
                ) : (
                  "GENERATE PATTERN"
                )}
                {/* Button glow effect */}
                <span className="absolute inset-0 bg-yellow-400 rounded opacity-0 group-hover:opacity-20 transition-opacity"></span>
              </button>
            </div>
          </form>
        </div>

        {/* Output */}
        {patternURL && (
          <div className="bg-black border-8 border-teal-400 p-4 md:p-6 relative">
            {/* Corner Decorations */}
            <div className="absolute top-2 left-2 w-3 h-3 border-2 border-yellow-400"></div>
            <div className="absolute top-2 right-2 w-3 h-3 border-2 border-yellow-400"></div>
            <div className="absolute bottom-2 left-2 w-3 h-3 border-2 border-yellow-400"></div>
            <div className="absolute bottom-2 right-2 w-3 h-3 border-2 border-yellow-400"></div>

            <h3 className="text-yellow-300 text-center mb-4 text-sm">
              GENERATED PATTERN
            </h3>
            <div className="flex justify-center">
              <img
                src={`http://localhost:5001${patternURL}`}
                alt="Generated Pattern"
                className="pixelated-image border-2 border-pink-400"
                style={{
                  maxWidth: "100%",
                  height: "auto",
                }}
              />
            </div>

            {/* Download Button */}
            <div className="text-center mt-4">
              <a
                href={`http://localhost:5001${patternURL}`}
                download="crochet_pattern.png"
                className="inline-block arcade-button bg-teal-500 text-black border-4 border-yellow-400 px-6 py-2
                         hover:bg-teal-400 hover:scale-105 transition-all duration-150 text-sm"
              >
                DOWNLOAD PATTERN
              </a>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-12 text-center text-xs text-gray-500">
        <p>iCrochet • Retro Pattern Generator</p>
      </div>
    </div>
  );
}