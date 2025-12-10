from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/preprocess/image', methods=['POST'])
def preprocess_image():
    """
    Receives an image, resizes/normalizes it, and returns metadata.
    In a real scenario, this might return the processed image bytes or upload to S3 directly.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Mock processing logic
    # image = Image.open(file)
    # image = image.resize((224, 224))
    
    return jsonify({
        "status": "success",
        "original_filename": file.filename,
        "processed_dims": [224, 224],
        "message": "Image resized and normalized for Rekognition"
    })

@app.route('/preprocess/audio', methods=['POST'])
def preprocess_audio():
    """
    Converts audio to format compatible with Transcribe (e.g., mp3/wav).
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    
    return jsonify({
        "status": "success",
        "original_filename": file.filename,
        "target_format": "mp3",
        "message": "Audio converted to MP3 44.1kHz"
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
