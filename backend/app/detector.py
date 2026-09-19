from ultralytics import YOLO

model = YOLO("best.pt")


def detect_pothole(image_path):
    results = model(image_path, conf=0.50)

    highest_confidence = 0.0

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            if class_id == 2 and confidence > highest_confidence:
                highest_confidence = confidence

    return highest_confidence