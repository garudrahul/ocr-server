from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
from PIL import Image
import io
import os
import re

app = Flask(__name__)
CORS(app)

# Initialize EasyOCR Reader (English)
def get_reader():
    return easyocr.Reader(['en'])

@app.route('/verify', methods=['POST'])
def verify_text():
    reader = get_reader()  # Load model only here
    if 'image' not in request.files:
        return jsonify({"error": "Image is required"}), 400
    if 'texts' not in request.form:
        return jsonify({"error": "JSON data with 'texts' is required"}), 400

    # Retrieve image and texts
    image_file = request.files['image']
    texts = request.form['texts']  # Retrieve texts as string
    user_texts = texts.strip().lower().split(',')  # Split the texts if they are separated by commas

    image_bytes = image_file.read()

    # Extract text with bounding boxes
    results = reader.readtext(image_bytes)

    # Extract individual words and clean them
    words = []
    for bbox, text, prob in results:
        cleaned_text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        words.extend(cleaned_text.strip().lower().split())  # Split into words

    # Check if each user_text is in the extracted words
    matches = {text: text in words for text in user_texts}

    return jsonify({
        "extracted_words": words,
        "matches": matches
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
