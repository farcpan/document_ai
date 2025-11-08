import argparse
import json
import cv2
from ultralytics import YOLO

MODEL_PATH = "./best.pt"

def run_inference(input_image_path: str):
    print(f"[INFO] loading model: {MODEL_PATH}")
    model = YOLO(MODEL_PATH)

    print(f"[INFO] reading image: {input_image_path}")
    img = cv2.imread(input_image_path)
    if img is None:
        raise FileNotFoundError(f"Failed to read image: {input_image_path}")

    print("[INFO] running inference...")
    results = model(input_image_path)
    result = results[0]

    response_data = []
    for box in result.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = result.names[cls_id]
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

        response_data.append({
            "x1": x1, "y1": y1,
            "x2": x2, "y2": y2,
            "conf": conf,
            "label": label,
        })

    return response_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YOLO inference runner")
    parser.add_argument("--image", required=True, help="Path to input image file")
    parser.add_argument("--out", default="result.json")
    args = parser.parse_args()

    result = run_inference(args.image)
    print(json.dumps(result, ensure_ascii=False))
