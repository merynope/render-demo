from flask import Flask, request, jsonify, render_template
import easyocr
import cv2
from werkzeug.utils import secure_filename
import os
from roboflow import Roboflow
import re
import dill
import requests
import numpy as np
from inference_sdk import InferenceHTTPClient

# Initialize Flask app
app = Flask(__name__)

# Initialize the InferenceHTTPClient with your API URL and API key
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="sATFGANLTgmF0sjtac0E"
)

# Define the OCR model function (this assumes you already have a saved model)
def ocr_model(image_path):
    # Call the Roboflow inference
    result = CLIENT.infer(image_path, model_id="expiredatedetection/4")

    # Print result to check its structure
    print(result)

    # Assuming result is a dictionary-like object and contains 'predictions'
    predictions = result.get('predictions', [])  # Safely access predictions

    # Process predictions
    extracted_dates = []
    reader = easyocr.Reader(['en'])  # Initialize EasyOCR Reader

    for prediction in predictions:
        x_center = prediction["x"]
        y_center = prediction["y"]
        box_width = prediction["width"]
        box_height = prediction["height"]

        top_left_x = int(x_center - box_width / 2)
        top_left_y = int(y_center - box_height / 2)
        bottom_right_x = int(x_center + box_width / 2)
        bottom_right_y = int(y_center + box_height / 2)

        # Read and preprocess the cropped region
        image = cv2.imread(image_path)
        cropped_image = image[top_left_y:bottom_right_y, top_left_x:bottom_right_x]
        gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
        _, processed_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # OCR on the processed image
        result = reader.readtext(processed_image)

        for bbox, text, confidence in result:
            date_match_ymd = re.match(r"(\d{4})[.,]?\s*(\d{2})[.,]?\s*(\d{2})(?:/)?", text)
            date_match_dmy = re.match(r"(\d{2})[.,]?\s*(\d{2})[.,]?\s*(\d{4})(?:/)?", text)

            if date_match_ymd:
                year = date_match_ymd.group(1)
                month = date_match_ymd.group(2)
                day = date_match_ymd.group(3)
                extracted_dates.append({"year": year, "month": month, "day": day})

            elif date_match_dmy:
                day = date_match_dmy.group(1)
                month = date_match_dmy.group(2)
                year = date_match_dmy.group(3)
                extracted_dates.append({"year": year, "month": month, "day": day})

    return extracted_dates

# Define a route for the index page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle image upload and process the image
@app.route('/process', methods=['POST'])
def process_image():
    # Check if an image was uploaded
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']

    # If no file is selected, send an error message
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the file to the server
    filename = secure_filename(file.filename)
    file_path = os.path.join('uploads', filename)
    file.save(file_path)

    # Process the uploaded image using the OCR model
    dates = ocr_model(file_path)
    print(dates)

    # Return results to render in the HTML page
    return render_template('index.html', dates=dates)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
