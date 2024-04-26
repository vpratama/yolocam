import cv2
import json
from ultralytics import YOLO
import datetime

now = datetime.datetime.now()

# Load the YOLOv8 model
model = YOLO('yolov8n-seg.pt')

# Set up the RTMP stream
rtmp_stream = "rtmp://localhost:1935"

# Open the RTMP stream
cap = cv2.VideoCapture(rtmp_stream)

# Set up the JSON file to save the results
json_file = "segmentation.json"

# Define the font and scale for the timestamp
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.5

while cap.isOpened():
    # Read a frame from the RTMP stream
    success, frame = cap.read()

    if success:
        now = datetime.datetime.now()
        
        # Convert the frame to HSV for color segmentation
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define the color ranges for segmentation
        lower_street = (0, 0, 100)
        upper_street = (100, 100, 255)
        lower_field = (30, 100, 100)
        upper_field = (80, 255, 255)
        lower_crossroad = (0, 0, 100)
        upper_crossroad = (100, 100, 255)
        lower_building = (50, 50, 50)
        upper_building = (150, 150, 150)
        lower_sky = (100, 100, 200)
        upper_sky = (255, 255, 255)

        # Perform color segmentation
        mask_street = cv2.inRange(hsv, lower_street, upper_street)
        mask_field = cv2.inRange(hsv, lower_field, upper_field)
        mask_crossroad = cv2.inRange(hsv, lower_crossroad, upper_crossroad)
        mask_building = cv2.inRange(hsv, lower_building, upper_building)
        mask_sky = cv2.inRange(hsv, lower_sky, upper_sky)

        # Convert the grayscale masks to single-channel BGR images
        mask_street = cv2.cvtColor(mask_street, cv2.COLOR_GRAY2BGR)
        mask_field = cv2.cvtColor(mask_field, cv2.COLOR_GRAY2BGR)
        mask_crossroad = cv2.cvtColor(mask_crossroad, cv2.COLOR_GRAY2BGR)
        mask_building = cv2.cvtColor(mask_building, cv2.COLOR_GRAY2BGR)
        mask_sky = cv2.cvtColor(mask_sky, cv2.COLOR_GRAY2BGR)

        # Run YOLOv8 inference on the segmented frames
        results_street = model(mask_street)
        results_field = model(mask_field)
        results_crossroad = model(mask_crossroad)
        results_building = model(mask_building)
        results_sky = model(mask_sky)

        # Visualize the results on the original frame
        annotated_frame = results_street[0].plot()
        annotated_frame = results_field[0].plot()
        annotated_frame = results_crossroad[0].plot()
        annotated_frame = results_building[0].plot()
        annotated_frame = results_sky[0].plot()

        # Add the timestamp to the frame
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(annotated_frame, timestamp, (10, 30), font, font_scale, (0, 255, 0), 1, cv2.LINE_AA)


        # Save the results to the JSON file
        with open(json_file, 'a') as f:
            json.dump(results_street[0].boxes.xyxy.tolist(), f)
            f.write('\n')
            json.dump(results_field[0].boxes.xyxy.tolist(), f)
            f.write('\n')
            json.dump(results_crossroad[0].boxes.xyxy.tolist(), f)
            f.write('\n')
            json.dump(results_building[0].boxes.xyxy.tolist(), f)
            f.write('\n')
            json.dump(results_sky[0].boxes.xyxy.tolist(), f)
            f.write('\n')

        # Display the annotated frame
        cv2.imshow("Autonomous Driving", annotated_frame)

        # Exit on key press
        if cv2.waitKey(1) == ord('q'):
            break

# Release the RTMP stream and close the window
cap.release()
cv2.destroyAllWindows()