
import argparse
import cv2
import json
import os
import subprocess


RESULT_JSON = "result.json"


def run_container(image_filename):
    """
    Docker コンテナを実行して推論結果 JSON を生成する
    """
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{os.getcwd()}:/app",
        "yolo-local",
        "python", "app.py",
        "--image", f"/app/{image_filename}",
        "--out", f"/app/{RESULT_JSON}"
    ]

    print("[INFO] Running container...")
    subprocess.run(cmd, check=True)
    print("[INFO] Container finished.")


def draw_results(image_filename):
    """
    result.json を読み込み、画像に描画して可視化
    """
    print("[INFO] Loading inference result...")

    with open(RESULT_JSON, "r", encoding="utf-8") as f:
        results = json.load(f)

    img = cv2.imread(image_filename)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_filename}")

    for obj in results:
        x1, y1 = obj["x1"], obj["y1"]
        x2, y2 = obj["x2"], obj["y2"]
        label = obj["label"]
        conf = obj["conf"]

        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, f"{label} {conf:.2f}",
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 255, 0),
                    2)

    print("[INFO] Showing result...")
    cv2.imshow("YOLO Result", img)
    cv2.waitKey(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YOLO inference runner")
    parser.add_argument("--image", required=True, help="Path to input image file")
    args = parser.parse_args()
    image_path = args.image

    run_container(image_filename=image_path)
    draw_results(image_filename=image_path)
