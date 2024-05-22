from ultralytics import YOLO
import json
import datetime
import cv2
import numpy as np
import time

# Load YOLO model
model = YOLO('yolov8n.pt')

# Open the RTMP stream
cap = cv2.VideoCapture("rtmp://167.205.66.10:1935")

# Create a JSON file to save the results
json_file = None

def get_label(class_id, yolo_classes):
    return yolo_classes[class_id]

while True:
    # Create a JSON file with timestamp
    json_filename = f"data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    json_file = open("video/" + json_filename, "w")

    # Create a VideoWriter object to save the video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_filename = f"data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    video_writer = cv2.VideoWriter("video/" + video_filename, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

    start_time = time.time()
    while time.time() - start_time < 30:  # Capture for 30 seconds
        # Read a frame from the stream
        ret, frame = cap.read()

        # Check if the frame was successfully read
        if not ret:
            print("Error: Could not read frame from stream")
            break

        # Perform object detection on the frame
        results = model(frame)

        # Extract the detection results
        detections = []
        for result in results:
            x1, y1, x2, y2 = result.boxes.xyxy[0]
            confidence = result.boxes.conf[0]
            class_id = result.boxes.cls[0]
            name = get_label(int(class_id), model.names)
            detections.append({
                "x1": int(x1),
                "y1": int(y1),
                "x2": int(x2),
                "y2": int(y2),
                "confidence": float(confidence),
                "class_id": int(class_id),
                "name": name
            })

        # Save the detection results to the JSON file
        json.dump(detections, json_file)
        json_file.write("\n")

        # Display the frame with bounding boxes
        for detection in detections:
            x1, y1, x2, y2 = detection["x1"], detection["y1"], detection["x2"], detection["y2"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Write the frame to the video
        video_writer.write(frame)

    # Release the resources
    cap.release()
    cv2.destroyAllWindows()
    json_file.close()
    video_writer.release()

    # Wait for 10 seconds before restarting
    time.sleep(10)

    # Reopen the RTMP stream
    cap = cv2.VideoCapture("rtmp://167.205.66.10:1935")