from ultralytics import YOLO

# Load YOLO model
model = YOLO('yolov8n.pt')

def predict_and_save(model, source, save_path, show=True, imgsz=320, conf=0.5):
    results = model.predict(source, show=show, imgsz=imgsz, conf=conf)

    for r in results:
        print(r)

# Example usage
predict_and_save(model, 'rtmp://localhost:1935', 'detection_results.json')
