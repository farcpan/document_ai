from ultralytics import YOLO
import boto3
import cv2
import json
import os

MODEL_PATH = "./runs/detect/train3/weights/best.pt"
TARGET_LABELS = ["image"]

BUCKET_NAME = os.environ['BUCKET_NAME']
s3_client = boto3.client('s3')


def run_inference(event, context):
    body = json.loads(event.get('body', '{}'))
    dirname = body.get("dirname")
    filename = body.get("filename")
    object_key = f"{dirname}/{filename}"
    extention = filename.split(".")[-1]
    print(f"dirname: {dirname}, filename: {filename}")

    input_image_path = f"/tmp/input.{extention}"
    print(f"input image path: {input_image_path}")
    s3_client.download_file(BUCKET_NAME, object_key, input_image_path)  # download & rename file to /tmp/input.png

    # loading model
    model = YOLO(MODEL_PATH)

    results = model(input_image_path, save=False)
    result = results[0]
    img = cv2.imread(input_image_path)

    response_data = []
    for box in result.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = result.names[cls_id]
        xyxy = box.xyxy[0].tolist()
        x1, y1, x2, y2 = map(int, xyxy)

        response_data.append({
            "x1": x1, "y1": y1,
            "x2": x2, "y2": y2,
            "conf": conf,
            "label": label,
        })

    return response_data


def handler(event=None, context=None):
    """Lambdaエントリーポイント"""
    response_list = run_inference(event=event, context=context)
    return {
        "statusCode": 200,
        "body": json.dumps(response_list)
    }


if __name__ == "__main__":
    # local test
    run_inference()