import subprocess
import json
import cv2
import os

IMAGE_PATH = "sample.jpg"          # 推論したい画像
RESULT_JSON = "result.json"        # コンテナが出力する結果


def run_container():
    """
    Docker コンテナを実行して推論結果 JSON を生成する
    """
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{os.getcwd()}:/app",
        "yolo-local",
        "python", "app.py",
        "--image", f"/app/{IMAGE_PATH}",
        "--out", f"/app/{RESULT_JSON}"
    ]

    print("[INFO] Running container...")
    subprocess.run(cmd, check=True)
    print("[INFO] Container finished.")


def draw_results():
    """
    result.json を読み込み、画像に描画して可視化
    """
    print("[INFO] Loading inference result...")

    with open(RESULT_JSON, "r", encoding="utf-8") as f:
        results = json.load(f)

    img = cv2.imread(IMAGE_PATH)
    if img is None:
        raise FileNotFoundError(f"Image not found: {IMAGE_PATH}")

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
    run_container()
    draw_results()
