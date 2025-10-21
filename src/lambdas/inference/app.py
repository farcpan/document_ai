from ultralytics import YOLO
import boto3
import cv2
import json
import os

MODEL_PATH = "./best.pt"
TARGET_LABELS = ["image"]

BUCKET_NAME = os.environ['BUCKET_NAME']
s3_client = boto3.client('s3')

"""
{
  "statusCode": 200,
  "body": "[{\"x1\": 49, \"y1\": 108, \"x2\": 412, \"y2\": 366, \"conf\": 0.8232455849647522, \"label\": \"image\"}, {\"x1\": 34, \"y1\": 579, \"x2\": 242, \"y2\": 709, \"conf\": 0.7119389176368713, \"label\": \"image\"}, {\"x1\": 430, \"y1\": 133, \"x2\": 694, \"y2\": 364, \"conf\": 0.6370389461517334, \"label\": \"text\"}, {\"x1\": 52, \"y1\": 425, \"x2\": 137, \"y2\": 438, \"conf\": 0.5911657810211182, \"label\": \"caption\"}, {\"x1\": 33, \"y1\": 710, \"x2\": 241, \"y2\": 774, \"conf\": 0.5703579783439636, \"label\": \"caption\"}, {\"x1\": 277, \"y1\": 398, \"x2\": 372, \"y2\": 414, \"conf\": 0.5374600887298584, \"label\": \"section-heading\"}, {\"x1\": 267, \"y1\": 416, \"x2\": 704, \"y2\": 629, \"conf\": 0.5330291986465454, \"label\": \"text\"}, {\"x1\": 50, \"y1\": 796, \"x2\": 136, \"y2\": 810, \"conf\": 0.4275764226913452, \"label\": \"section-heading\"}, {\"x1\": 52, \"y1\": 425, \"x2\": 137, \"y2\": 438, \"conf\": 0.4012201130390167, \"label\": \"section-heading\"}, {\"x1\": 38, \"y1\": 808, \"x2\": 238, \"y2\": 904, \"conf\": 0.3928162455558777, \"label\": \"table\"}, {\"x1\": 41, \"y1\": 819, \"x2\": 233, \"y2\": 905, \"conf\": 0.34649357199668884, \"label\": \"text\"}, {\"x1\": 431, \"y1\": 104, \"x2\": 571, \"y2\": 121, \"conf\": 0.33310988545417786, \"label\": \"section-heading\"}, {\"x1\": 61, \"y1\": 920, \"x2\": 93, \"y2\": 932, \"conf\": 0.2949292063713074, \"label\": \"caption\"}]"
}
"""


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