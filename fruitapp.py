from flask import Flask, render_template, Response, jsonify
import cv2
from datetime import datetime
from ultralytics import YOLO

# Initialize Flask app
app = Flask(__name__)

# Load the YOLOv8 model
model = YOLO('best.pt')  # Ensure that 'best.pt' is the trained model

# Capture video from the webcam
camera = cv2.VideoCapture(0)

# Data storage for analysis results
analysis_results = []

# Helper function to analyze a frame
def analyze_frame(frame):
    # Run inference
    results = model(frame)  # Perform inference
    detections = results[0].boxes  # Access bounding boxes from the first result

    # Parse results
    output = []
    for i in range(len(detections)):
        box = detections[i]  # Get bounding box
        produce = results[0].names[box.cls[0].item()]  # Get the class name
        freshness = box.conf[0].item()  # Get the confidence score
        timestamp = datetime.now().isoformat()

        # Assign expected lifespan based on produce type (example values, customize as needed)
        lifespan_mapping = {
            'broccoli': 5,
            'onion': 12,
            'papaya': 2
        }
        lifespan = lifespan_mapping.get(produce, 'N/A')

        # Append data to output
        output.append({
            'timestamp': timestamp,
            'produce': produce,
            'freshness': round(freshness * 10),  # Scale confidence to a 1-10 freshness score
            'lifespan': lifespan
        })
    return output

# Route to display the results in table format
@app.route('/findex')
def index():
    return render_template('findex.html', results=analysis_results)

# Generate video feed
def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Analyze the current frame when requested
            global analysis_results
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            current_results = analyze_frame(frame_rgb)
            analysis_results.extend(current_results)

            # Run YOLOv8 model inference on the frame
            results = model(frame)

            # Render the predictions on the frame (use results[0] if it's a list)
            frame = results[0].plot()  # Use plot() to render the results

            # Encode the frame
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Yield the frame for streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Video feed route
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# API to fetch results
@app.route('/results', methods=['GET'])
def get_results():
    return jsonify(analysis_results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
