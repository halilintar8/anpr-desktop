import cv2
import pytesseract
from ultralytics import YOLO
import torch
import re
import time
import csv
import os

# Indonesian plate regex:
# 1-2 letters + 1-4 digits + optional 1-3 letters
PLATE_REGEX = r'^[A-Z]{1,2}[0-9]{1,4}[A-Z]{0,3}$'

device = 'cpu'
print("Using device:", device)

model = YOLO("models/yolov8n.pt")

# ===== CAMERA DETECTION =====
def get_available_cameras(max_tested=6):
    camera_indexes = []

    for index in range(max_tested):
        cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
        if not cap.isOpened():
            cap.release()
            continue

        ret, frame = cap.read()
        if ret:
            camera_indexes.append(index)

        cap.release()

    return camera_indexes

cameras = get_available_cameras()

if not cameras:
    print("No cameras found!")
    exit()

current_cam_index = 0
cap = cv2.VideoCapture(cameras[current_cam_index], cv2.CAP_V4L2)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Available cameras:", cameras)
print("Press Q to exit")
print("Press C to switch camera")
print("Press S to save detected plate")

# ===== PERFORMANCE SETTINGS =====
frame_count = 0
skip_frames = 4
imgsz = 320

last_plate = ""
last_plate_time = 0
ocr_cooldown = 0.8
# ================================

# ===== CSV SETUP =====
csv_file = "plates.csv"

if not os.path.exists(csv_file):
    with open(csv_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Plate Number", "Timestamp"])
# =====================

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))
    frame_count += 1

    if frame_count % skip_frames == 0:

        small = cv2.resize(frame, (320, 240))

        results = model.predict(
            small,
            imgsz=imgsz,
            conf=0.4,
            device=device,
            verbose=False
        )

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                x_scale = 640 / 320
                y_scale = 480 / 240

                x1 = int(x1 * x_scale)
                x2 = int(x2 * x_scale)
                y1 = int(y1 * y_scale)
                y2 = int(y2 * y_scale)

                plate_crop = frame[y1:y2, x1:x2]

                if plate_crop.size == 0:
                    continue

                current_time = time.time()

                if current_time - last_plate_time > ocr_cooldown:

                    gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)
                    gray = cv2.resize(gray, None, fx=2, fy=2)
                    _, thresh = cv2.threshold(
                        gray, 0, 255,
                        cv2.THRESH_BINARY + cv2.THRESH_OTSU
                    )

                    text = pytesseract.image_to_string(
                        thresh,
                        config='--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                    )

                    text = text.upper().replace(" ", "").strip()

                    if re.match(PLATE_REGEX, text):
                        last_plate = text
                        last_plate_time = current_time

                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)

    # Display detected plate
    if last_plate:
        cv2.putText(frame, f"Plate: {last_plate}",
                    (20,40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0,255,0),
                    2)

    # Show current camera
    cv2.putText(frame, f"Camera: /dev/video{cameras[current_cam_index]}",
                (20,470),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255,255,0),
                2)

    cv2.putText(frame, "Press C: Switch | S: Save | Q: Quit",
                (20,440),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255,255,255),
                2)

    cv2.imshow("Indonesia ANPR", frame)

    key = cv2.waitKey(1) & 0xFF

    # Quit
    if key == ord('q'):
        break

    # Switch camera
    if key == ord('c'):
        cap.release()
        current_cam_index = (current_cam_index + 1) % len(cameras)
        cap = cv2.VideoCapture(cameras[current_cam_index], cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Save detected plate
    if key == ord('s'):
        if last_plate:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            with open(csv_file, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([last_plate, timestamp])

            print(f"Saved: {last_plate} at {timestamp}")
        else:
            print("No plate detected to save.")

cap.release()
cv2.destroyAllWindows()

if torch.cuda.is_available():
    torch.cuda.empty_cache()