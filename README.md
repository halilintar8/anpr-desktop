
---

````markdown
# 🇮🇩 Indonesia ANPR Desktop

Automatic Number Plate Recognition (ANPR) system using **YOLOv8** for detection and **Tesseract OCR** for license plate text recognition.

This project runs in real-time using a USB or internal webcam on Linux.

---

## ✨ Features

- Real-time license plate detection
- OCR-based plate number recognition
- Multi-camera support
- Save detected plates to CSV file
- Lightweight and CPU-friendly
- GPU acceleration (optional)

---

## 📋 Requirements

- Ubuntu 20.04 / 22.04 / 24.04 (recommended)
- Python 3.10 – 3.12
- Webcam (USB or internal)
- Internet connection (first installation only)

---

# 🚀 Installation Guide

---

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/anpr-desktop.git
cd anpr-desktop
````

Or download the ZIP and extract it.

---

## 2️⃣ Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate 
# or "source venv/bin/activate.fish" if you use fish shell
```

You should now see:

```bash
(venv)
```

---

## 3️⃣ Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3-pip tesseract-ocr libgl1 fonts-dejavu
```

Verify Tesseract installation:

```bash
tesseract --version
```

---

## 4️⃣ Install Python Dependencies

### If using CPU only:

```bash
pip install -r requirements.txt
```

---

### If using NVIDIA GPU (CUDA 11.8):

Install PyTorch first:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

Then install remaining packages:

```bash
pip install -r requirements.txt
```

---

## 5️⃣ Verify Camera (Linux Only)

List detected cameras:

```bash
ls /dev/video*
```

Get detailed information:

```bash
v4l2-ctl --list-devices
```

Example:

```
C270 HD WEBCAM:
    /dev/video2
```

---

## 6️⃣ Run the Application

```bash
python app.py
```

Expected output:

```
Using device: cpu
Available cameras: [0, 2]
Press Q to exit
Press C to switch camera
Press S to save detected plate
```

---

# 🎮 Controls

| Key | Function                   |
| --- | -------------------------- |
| C   | Switch camera              |
| S   | Save detected plate to CSV |
| Q   | Quit application           |

---

# 📁 Output

Detected plates are saved to:

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

# ⚡ Performance Optimization

If detection feels slow:

* Use 640x480 resolution
* Reduce YOLO image size to 320
* Close other camera apps
* Use GPU version of PyTorch

---

# 🛠 Troubleshooting

## Camera Cannot Open

Check available devices:

```bash
v4l2-ctl --list-devices
```

Update camera index in `app.py` if needed.

---

## Qt Font Warning

If you see:

```
QFontDatabase: Cannot find font directory...
```

Install fonts:

```bash
sudo apt install fonts-dejavu
```

---

## Torch Installation Issues

Reinstall PyTorch:

```bash
pip uninstall torch torchvision -y
pip install torch torchvision
```

---

# 📦 Project Structure

```
anpr-desktop/
│
├── app.py
├── requirements.txt
├── plates.csv
├── models/
│   └── yolov8n.pt
└── README.md
```

---

# 🏁 Finished

Your ANPR system is now ready to:

* Detect license plates
* Recognize plate numbers
* Switch cameras
* Save results to CSV

---

## 📌 Author

Muhammad Bintang – ANPR Desktop Project

```

# 📄 Also Create `requirements.txt`

Make sure you create this file:

ultralytics
opencv-python
pytesseract

```

---

## 📌 Notes

```

# 📄 do this if you want to delete venv folder because of its large size :

pip freeze > requirements.txt (if needed)
deactivate
rm -rf venv

# 📄 create venv again :

python3 -m venv venv
source venv/bin/activate.fish   # if you use fish shell
pip install -r requirements.txt

```

---

