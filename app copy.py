import cv2
import easyocr
from ultralytics import YOLO
import torch
import re

# Indonesian plate regex:
# 1-2 letters + 1-4 digits + optional 1-3 letters
PLATE_REGEX = r'^[A-Z]{1,2}\s?[0-9]{1,4}\s?[A-Z]{0,3}$'

# device = 'cuda' if torch.cuda.is_available() else 'cpu'
device = 'cpu'
print("Using device:", device)

# Load YOLO nano model
model = YOLO("models/yolov8n.pt")

# Load OCR
# reader = easyocr.Reader(['en'], gpu=torch.cuda.is_available())
reader = easyocr.Reader(['en'], gpu=False)

# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(2, cv2.CAP_V4L2)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

if not cap.isOpened():
    print("Camera not found!")
    exit()

print("Press Q to exit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))

    results = model.predict(
        frame,
        # imgsz=640,
        imgsz=512,        
        conf=0.4,
        device=device,
        verbose=False
    )

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            plate_crop = frame[y1:y2, x1:x2]

            if plate_crop.size == 0:
                continue

            ocr_results = reader.readtext(plate_crop)

            for (_, text, prob) in ocr_results:
                text = text.upper().replace(" ", "")

                if prob > 0.5 and re.match(PLATE_REGEX, text):
                    cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
                    cv2.putText(frame, text,
                                (x1, y1-10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.8,
                                (0,255,0),
                                2)

    cv2.imshow("Indonesia ANPR - Press Q to exit", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

if torch.cuda.is_available():
    torch.cuda.empty_cache()

