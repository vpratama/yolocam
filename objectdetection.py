from ultralytics import YOLO
import json
import datetime

now = datetime.datetime.now()

# Load YOLO model
model = YOLO('yolov8n.pt')

def predict_and_save(model, source, save_path, show=True, imgsz=320, conf=0.5):
    results = model.predict(source, show=show, imgsz=imgsz, conf=conf)

    # Convert results to a list of dictionaries
    results_list = []
    for r in results:
        result_dict = {
            'timestamp': now.timestamp(),
            'image_path': r.ims[0].stem,
            'detections': []
        }
        for det in r.xyxy:
            detection_dict = {
                'class_id': int(det[-1]),
                'confidence': float(det[-2]),
                'bbox': [float(x) for x in det[:4]]
            }
            result_dict['detections'].append(detection_dict)
        results_list.append(result_dict)

    # Save results to JSON file
    with open(save_path, 'w') as f:
        json.dump(results_list, f, indent=4)

# Example usage
predict_and_save(model, 'rtmp://localhost:1935', 'objectdetection.json')