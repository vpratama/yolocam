import cv2
import pika
import json
from ultralytics import YOLO
from scipy.spatial import distance as dist
import argparse
import datetime
import time  # Import time module

# Camera
focal_length = 500

# Define real sizes for different classes (in meters)
real_sizes = {
    'person': 1.65,
    'car': 1.5,
    'bicycle': 1.0,
    'dog': 0.5,
    'cat': 0.3,
    'truck': 2.0,
    'bus': 3.5,
    'motorcycle': 1.2,
    'sheep': 1.0,
    'horse': 1.5,
    'elephant': 3.0,
    'giraffe': 5.5,
    'table': 0.75,
    'chair': 0.45,
    'sofa': 0.85,
    'tv': 1.0,
    'refrigerator': 1.8,
    'door': 2.0,
    'window': 1.5,
    'tree': 5.0,
    'flower': 0.3,
    'basketball': 0.24,
    'soccer_ball': 0.22,
    'apple': 0.1,
    'banana': 0.2,
    'bottle': 0.25,
    'cup': 0.1,
    'pencil': 0.19,
    'book': 0.25,
    'laptop': 0.02,
    'backpack': 0.5,
    'stool': 0.75,
    'bench': 0.9,
    'kitchen_island': 0.9,
    'fire_hydrant': 1.0,
    'traffic_light': 2.5,
    'sign': 1.5,
    'cactus': 1.0,
    'palm_tree': 6.0,
    'fence': 1.5,
    'swing': 1.5,
    'ladder': 2.0,
    'scooter': 0.9,
    'skateboard': 0.1,
}

# Argument parser setup
parser = argparse.ArgumentParser(description='Object Detection with YOLO and RabbitMQ')
parser.add_argument('video_source', type=int, help='Camera index (e.g., 0 for the first camera)')
parser.add_argument('queue_name', type=str, help='RabbitMQ queue name (e.g., camera-front)')

args = parser.parse_args()

# Initialize RabbitMQ connection with specified parameters
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        port=5672,
        virtual_host='/',
        credentials=pika.PlainCredentials('camera', 'camera'),
        heartbeat=600
    )
)
channel = connection.channel()
channel.queue_declare(queue=args.queue_name, durable = True, auto_delete = True)  # Declare the queue using the argument

# Load YOLO model
model = YOLO("yolo11n.pt")

# Capture video from the specified camera
cap = cv2.VideoCapture(args.video_source)
if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

def get_label(class_id, yolo_classes):
    return yolo_classes[class_id]

while True:
    # Record the start time
    start_time = time.time()

    # Read a frame from the camera
    ret, frame = cap.read()
    if not ret:
        break

    # Perform object detection
    results = model(frame)

    # Prepare detection data for RabbitMQ
    detection_data = []
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0]  # Get bounding box coordinates
            confidence = box.conf[0]  # Get confidence score
            label = model.names[int(box.cls[0])]  
            class_id = result.boxes.cls[0]
            name = get_label(int(class_id), model.names)
            box_size = dist.euclidean((x1, y1), (x2, y2))

            # Get the real size for the detected object
            real_size = real_sizes.get(label, 1.0)  # Default to 1.0 if label not found
            distance = (real_size * focal_length) / box_size

            # Append detection data
            detection_data.append({
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "class_id": int(class_id),
                'label': label,
                "name": name,
                'confidence': confidence.item(),
                'box': [int(x1), int(y1), int(x2), int(y2)],
                "x1": int(x1),
                "y1": int(y1),
                "x2": int(x2),
                "y2": int(y2),
                "distance": distance
            })

    # Send detection data to RabbitMQ
    channel.basic_publish(
        exchange='amq.direct',
        routing_key=args.queue_name,
        body=json.dumps(detection_data)
    )

    # Display the frame with detections and additional data
    for detection in detection_data:
        x1, y1, x2, y2 = detection['box']
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        text = f"{detection['label']}: {detection['confidence']:.2f}, Distance: {detection['distance']:.2f}"
        cv2.putText(frame, text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("Image", frame)

    # Calculate the time taken to process the frame
    # elapsed_time = time.time() - start_time
    # wait_time = max(1, int(30 - elapsed_time * 1000))  # Calculate wait time in milliseconds
    # cv2.waitKey(wait_time)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
connection.close()