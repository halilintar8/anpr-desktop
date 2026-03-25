Here is a **clean, professional, step-by-step installation guide** you can copy directly into your `README.md`.

---

# 🇮🇩 Indonesia ANPR Desktop

Automatic Number Plate Recognition using YOLOv8 + Tesseract OCR

---

# 📋 Requirements

* Ubuntu 20.04 / 22.04 / 24.04 (recommended)
* Python 3.10 – 3.12
* Webcam (Logitech C270 or internal camera)
* Internet connection (for first install)

---

# 🚀 Step-by-Step Installation

---

## 1️⃣ Clone Project

```bash
git clone https://github.com/your-username/anpr-desktop.git
cd anpr-desktop
```

Or extract the project ZIP and enter the folder.

---

## 2️⃣ Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

Your terminal should now show:

```bash
(venv)
```

---

## 3️⃣ Install System Dependencies

Install required system packages:

```bash
sudo apt update
sudo apt install -y python3-pip tesseract-ocr libgl1 fonts-dejavu
```

Verify Tesseract:

```bash
tesseract --version
```

---

## 4️⃣ Install Python Dependencies

If you are using **CPU only**:

```bash
pip install torch torchvision
```

If you are using **NVIDIA GPU (CUDA 11.8)**:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

Then install the rest:

```bash
pip install ultralytics opencv-python pytesseract
```

---

## 5️⃣ Verify Camera Detection (Linux)

List available cameras:

```bash
ls /dev/video*
```

Detailed camera info:

```bash
v4l2-ctl --list-devices
```

Example output:

```
C270 HD WEBCAM:
    /dev/video2
```

Remember the correct `/dev/videoX`.

---

## 6️⃣ Run Application

```bash
python app.py
```

You should see:

```
Using device: cpu
Available cameras: [0, 2]
Press Q to exit
Press C to switch camera
Press S to save detected plate
```

---

# 🎮 Controls

| Key | Action                     |
| --- | -------------------------- |
| C   | Switch camera              |
| S   | Save detected plate to CSV |
| Q   | Quit application           |

---

# 📁 Output File

Detected plates are saved automatically to:

```
plates.csv
```

Example:

```
Plate Number,Timestamp
B1234XYZ,2026-02-28 19:41:22
D5678ABC,2026-02-28 19:42:10
```

---

# ⚡ Performance Tips

If camera is slow:

* Make sure resolution is set to 640x480
* Close other apps using the camera
* Use GPU version of PyTorch if available
* Reduce YOLO `imgsz` to 320 for faster detection

---

# 🛠 Troubleshooting

## Camera cannot open

Run:

```bash
v4l2-ctl --list-devices
```

Then update camera index inside `app.py`.

---

## Qt Font Warning

If you see:

```
QFontDatabase: Cannot find font directory...
```

Run:

```bash
sudo apt install fonts-dejavu
```

---

## EasyOCR / Torch Error

If you get torch or dependency errors:

```bash
pip uninstall torch torchvision -y
pip install torch torchvision
```

---

# 🧠 Project Structure

```
anpr-desktop/
│
├── app.py
├── plates.csv
├── models/
│   └── yolov8n.pt
├── README.md
└── venv/
```

---

# 🏁 Done!

Your ANPR system should now:

* Detect license plates
* Extract plate numbers
* Switch between cameras
* Save plate numbers to CSV

---

If you'd like, I can also generate:

* 📦 Docker setup
* 🖥 Windows installation guide
* 🎥 GPU acceleration guide
* 🏗 Production deployment guide

Just tell me which one you want.

