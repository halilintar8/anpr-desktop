# ============================================================
# INDONESIA ANPR - CPU STABLE VERSION (LINUX SAFE)
# ============================================================

# -------------------- FORCE CPU -----------------------------
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import cv2
import pytesseract
from ultralytics import YOLO
import torch
import re
import time
import csv
import sys

# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = "models/yolov8n.pt"
CSV_FILE = "plates.csv"

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

IMG_SIZE = 320
SKIP_FRAMES = 5
CONFIDENCE = 0.4
OCR_COOLDOWN = 1.0

PLATE_REGEX = r'^[A-Z]{1,2}[0-9]{1,4}[A-Z]{0,3}$'

DEVICE = "cpu"
print("Using device:", DEVICE)

# ============================================================
# CAMERA HANDLING (LINUX SAFE - V4L2 ONLY)
# ============================================================

def detect_cameras(max_index=5):
    valid_cameras = []

    for index in range(max_index):
        cap = cv2.VideoCapture(index, cv2.CAP_V4L2)

        if not cap.isOpened():
            cap.release()
            continue

        ret, frame = cap.read()

        if ret and frame is not None:
            valid_cameras.append(index)

        cap.release()

    return valid_cameras


def open_camera(index):
    cap = cv2.VideoCapture(index, cv2.CAP_V4L2)

    if not cap.isOpened():
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    return cap

# ============================================================
# CSV HANDLING
# ============================================================

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Plate Number", "Timestamp"])


def save_plate(plate):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([plate, timestamp])

    print(f"[SAVED] {plate} at {timestamp}")

# ============================================================
# OCR PROCESSING
# ============================================================

def read_plate(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2)

    _, thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    text = pytesseract.image_to_string(
        thresh,
        config="--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    )

    text = text.upper().replace(" ", "").strip()

    if re.match(PLATE_REGEX, text):
        return text

    return None

# ============================================================
# MAIN APPLICATION
# ============================================================

def main():

    # Check model
    if not os.path.exists(MODEL_PATH):
        print("Model file not found:", MODEL_PATH)
        sys.exit(1)

    print("Loading YOLO model...")
    model = YOLO(MODEL_PATH)

    init_csv()

    cameras = detect_cameras()

    if not cameras:
        print("No working camera detected.")
        sys.exit(1)

    print("Available cameras:", cameras)
    print("Q: Quit | C: Switch Camera | S: Save Plate")

    cam_index = 0
    cap = open_camera(cameras[cam_index])

    if cap is None:
        print("Failed to open camera.")
        sys.exit(1)

    frame_count = 0
    last_plate = ""
    last_detect_time = 0

    # ========================================================
    # LOOP
    # ========================================================

    while True:

        ret, frame = cap.read()
        if not ret:
            print("Camera read error.")
            break

        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
        frame_count += 1

        # Run detection only every N frames (CPU optimization)
        if frame_count % SKIP_FRAMES == 0:

            small = cv2.resize(frame, (320, 240))

            results = model.predict(
                small,
                imgsz=IMG_SIZE,
                conf=CONFIDENCE,
                device=DEVICE,
                verbose=False
            )

            for r in results:
                for box in r.boxes:

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    # Scale back coordinates
                    x_scale = FRAME_WIDTH / 320
                    y_scale = FRAME_HEIGHT / 240

                    x1 = int(x1 * x_scale)
                    x2 = int(x2 * x_scale)
                    y1 = int(y1 * y_scale)
                    y2 = int(y2 * y_scale)

                    plate_crop = frame[y1:y2, x1:x2]

                    if plate_crop.size == 0:
                        continue

                    current_time = time.time()

                    # Prevent repeated OCR
                    if current_time - last_detect_time > OCR_COOLDOWN:
                        text = read_plate(plate_crop)

                        if text:
                            last_plate = text
                            last_detect_time = current_time

                    # Draw box
                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2
                    )

        # ================= DISPLAY =================

        if last_plate:
            cv2.putText(
                frame,
                f"Plate: {last_plate}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

        cv2.putText(
            frame,
            f"Camera: {cameras[cam_index]}",
            (20, 470),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "C: Switch | S: Save | Q: Quit",
            (20, 440),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.imshow("Indonesia ANPR - CPU Stable", frame)

        key = cv2.waitKey(1) & 0xFF

        # Quit
        if key == ord("q"):
            break

        # Switch Camera
        if key == ord("c"):
            cap.release()

            cam_index = (cam_index + 1) % len(cameras)
            new_cap = open_camera(cameras[cam_index])

            if new_cap is None:
                print("Failed to switch camera.")
            else:
                cap = new_cap
                print("Switched to camera", cameras[cam_index])

        # Save Plate
        if key == ord("s"):
            if last_plate:
                save_plate(last_plate)
            else:
                print("No plate detected.")

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()