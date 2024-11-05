import cv2
import pika
import json
from ultralytics import YOLO
from scipy.spatial import distance as dist

# Camera
focal_length = 500

# Define real sizes for different classes (in meters)
real_sizes = {
    'person': 1.8,          # height of an average person
    'car': 1.5,             # average height of a car
    'bicycle': 1.0,         # average height of a bicycle
    'dog': 0.5,             # average height of a dog
    'cat': 0.3,             # average height of a cat
    'truck': 2.0,           # average height of a truck
    'bus': 3.5,             # average height of a bus
    'motorcycle': 1.2,      # average height of a motorcycle
    'sheep': 1.0,           # average height of a sheep
    'horse': 1.5,           # average height of a horse
    'elephant': 3.0,        # average height of an elephant
    'giraffe': 5.5,         # average height of a giraffe
    'table': 0.75,          # average height of a table
    'chair': 0.45,          # average height of a chair
    'sofa': 0.85,           # average height of a sofa
    'tv': 1.0,              # average height of a TV (from floor to top)
    'refrigerator': 1.8,    # average height of a refrigerator
    'door': 2.0,            # average height of a door
    'window': 1.5,          # average height of a window
    'tree': 5.0,            # average height of a small tree
    'flower': 0.3,          # average height of a flower
    'basketball': 0.24,     # average height of a basketball
    'soccer_ball': 0.22,    # average height of a soccer ball
    'apple': 0.1,           # average height of an apple
    'banana': 0.2,          # average height of a banana
    'bottle': 0.25,         # average height of a standard bottle
    'cup': 0.1,             # average height of a cup
    'pencil': 0.19,         # average height of a pencil
    'book': 0.25,           # average height of a book
    'laptop': 0.02,         # average height of a laptop
    'backpack': 0.5,        # average height of a backpack
    'stool': 0.75,          # average height of a stool
    'bench': 0.9,           # average height of a bench
    'kitchen_island': 0.9,  # average height of a kitchen island
    'fire_hydrant': 1.0,    # average height of a fire hydrant
    'traffic_light': 2.5,    # average height of a traffic light
    'sign': 1.5,            # average height of a road sign
    'cactus': 1.0,          # average height of a cactus
    'palm_tree': 6.0,       # average height of a palm tree
    'fence': 1.5,           # average height of a fence
    'swing': 1.5,           # average height of a swing
    'ladder': 2.0,          # average height of a ladder
    'scooter': 0.9,         # average height of a scooter
    'skateboard': 0.1,      # average height of a skateboard
    # Add other classes and their real sizes as needed
}

# Initialize RabbitMQ connection with specified parameters
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        port=5672,
        virtual_host='/',
        credentials=pika.PlainCredentials('camera', 'camera')
    )
)
channel = connection.channel()
channel.queue_declare(queue='camera')  # Declare the queue if it doesn't exist

# Load YOLOv8 model
model = YOLO("yolov8n.pt")  # Ensure you have the YOLOv8 weights file

# Capture video from camera
cap = cv2.VideoCapture(0)

def get_label(class_id, yolo_classes):
    return yolo_classes[class_id]

while True:
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
            label = model.names[int(box.cls[0])]  # Get class label
            class_id = result.boxes.cls[0]
            name = get_label(int(class_id), model.names)
            box_size = dist.euclidean((x1, y1), (x2, y2))

            # Get the real size for the detected object
            real_size = real_sizes.get(label, 1.0)  # Default to 1.0 if label not found
            distance = (real_size * focal_length) / box_size

            # Append detection data
            detection_data.append({
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
        routing_key='camera1',
        body=json.dumps(detection_data)
    )

    # Display the frame with detections and additional data
    for detection in detection_data:
        x1, y1, x2, y2 = detection['box']
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        text = f"{detection['label']}: {detection['confidence']:.2f}, Distance: {detection['distance']:.2f}"
        cv2.putText(frame, text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("Image", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
connection.close()