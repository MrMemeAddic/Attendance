<div align="center">

# ⬡ Jagte Raho
### Real-Time Face Recognition Attendance System

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.11+-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-0F9D58?style=for-the-badge&logo=google&logoColor=white)](https://mediapipe.dev/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.13+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

*A modern, desktop face recognition attendance system with anti-spoofing liveness detection*

</div>

---

## 📖 Overview

**Jagte Raho** (Hindi: *Stay Vigilant*) is a fully offline, desktop attendance management system powered by deep learning. It uses **FaceNet** embeddings for robust face recognition and **MediaPipe** for real-time face detection and 478-point landmark tracking. An active **liveness detection** module prevents spoofing attacks using Eye Aspect Ratio (EAR) blink analysis.

All data is stored locally in SQLite — no cloud, no subscriptions, no privacy concerns.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **FaceNet Embeddings** | 512-dim InceptionResnetV1 embeddings for high-accuracy recognition |
| 👁️ **Liveness Detection** | Anti-spoofing via real-time blink detection (EAR algorithm) |
| ⚡ **Two-Stage Detection** | Fast BlazeFace for bounding boxes; full 478-pt landmarks only when needed |
| 📊 **Attendance Logging** | Daily CSV **and** styled XLSX reports with deduplication |
| 🗃️ **SQLite Database** | Embedded, zero-config storage for persons, embeddings, and recognition logs |
| 🎨 **Dark-themed GUI** | Tkinter 3-tab interface (Register / Recognize / Manage) |
| 🔄 **Auto Model Download** | MediaPipe TFLite models downloaded automatically on first run |
| 🧵 **Non-blocking I/O** | Recognition logs written asynchronously to avoid UI stutter |
| 📁 **Export Reports** | Generate PDF/XLSX attendance reports via `generate_report.py` |

---

## 🖥️ Screenshots

> *The app launches with a splash screen while the FaceNet model loads, then presents a tabbed interface.*

| Register | Recognize | Manage |
|---|---|---|
| Register new faces from a webcam | Real-time recognition with liveness check | View, search, and delete registered persons |

---

## 🏗️ Architecture

```
Jagte_Raho/
├── main.py                  # Entry point — Tkinter App + splash screen
├── run.bat                  # Windows launcher (sets up Tcl/Tk paths)
├── requirements.txt         # Python dependencies
├── generate_report.py       # Standalone attendance report generator
├── tests_headless.py        # Headless test suite
│
├── core/                    # Business logic
│   ├── detector.py          # MediaPipe face detection (BlazeFace + FaceLandmarker)
│   ├── embedder.py          # FaceNet embedding extraction (facenet-pytorch)
│   ├── matcher.py           # Cosine-similarity face matching
│   ├── liveness.py          # Eye Aspect Ratio blink detection
│   ├── tracker.py           # Multi-face identity tracking across frames
│   ├── attendance.py        # Daily CSV + XLSX attendance logger
│   ├── database.py          # SQLite CRUD (persons, embeddings, recognition log)
│   └── _models/             # Auto-downloaded MediaPipe TFLite models
│
├── ui/                      # Tkinter panels
│   ├── register_panel.py    # Tab 1: Register new persons
│   ├── recognize_panel.py   # Tab 2: Live recognition feed
│   └── manage_panel.py      # Tab 3: Manage registered persons
│
└── data/
    ├── faces.db             # SQLite database (auto-created)
    └── attendance/          # Daily attendance files (auto-created)
        ├── attendance_YYYY-MM-DD.csv
        └── attendance_YYYY-MM-DD.xlsx
```

---

## 🚀 Getting Started

### Prerequisites

- **Windows 10/11** (tested on Windows with Python 3.14)
- **Python 3.14** — [Download](https://www.python.org/downloads/)
- A **webcam** connected to your machine

### 1. Clone the repository

```bash
git clone https://github.com/your-username/jagte-raho.git
cd jagte-raho
```

### 2. Create a virtual environment

```bash
py -3.14 -m venv .venv314
```

### 3. Install PyTorch (CPU)

```bash
.venv314\Scripts\pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

> 💡 For GPU support, visit [pytorch.org](https://pytorch.org/get-started/locally/) and select the appropriate CUDA version.

### 4. Install remaining dependencies

```bash
.venv314\Scripts\pip install -r requirements.txt
```

### 5. Launch the application

**Option A — Double-click launcher (recommended):**
```
run.bat
```

**Option B — Manual:**
```bash
.venv314\Scripts\python.exe main.py
```

> ⏳ On **first launch**, MediaPipe TFLite models are downloaded automatically (~15 MB). The splash screen will show while FaceNet initializes.

---

## 🎯 How to Use

### ➕ Register Tab
1. Enter the person's **full name**
2. Click **Start Camera** and position your face in the frame
3. Click **Capture** to collect face samples (multiple captures improve accuracy)
4. Click **Register** to save the person to the database

### 👁 Recognize Tab
1. Click **Start** to begin the live recognition feed
2. The system detects faces and prompts for a **liveness check** (blink detection)
3. Recognized persons are identified with a confidence score and logged to attendance
4. Attendance is recorded to daily `.csv` and `.xlsx` files with a 60-second cooldown per person

### 🗂 Manage Tab
- View all registered persons with their embedding count
- Search/filter by name
- Delete individuals from the database

---

## 🧠 Technical Details

### Face Recognition Pipeline

```
Camera Frame
     │
     ▼
BlazeFace Detection          ← Fast, ~30-60ms per frame
     │
     ▼
FaceNet Embedding            ← InceptionResnetV1, 512-dim vector
     │
     ▼
Cosine Similarity Matching   ← Against registered embeddings in SQLite
     │
     ▼
Identity + Confidence Score
```

### Liveness Detection (EAR)

The system uses the **Eye Aspect Ratio** algorithm (Soukupová & Čech, 2016):

```
EAR = (‖p2−p6‖ + ‖p3−p5‖) / (2 × ‖p1−p4‖)
```

- EAR drops significantly when the eye closes (blink)
- Requires **2 blinks within 8 seconds** to pass the liveness check
- Uses MediaPipe's 478-point FaceLandmarker for precise eye landmark extraction

### Database Schema

```sql
persons        (id, name, label, created_at)
embeddings     (id, person_id → persons, embedding BLOB, source, created_at)
recognition_log (id, person_id → persons, name, confidence, liveness, timestamp)
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `torch` | ≥ 2.11.0 | Deep learning backend |
| `torchvision` | ≥ 0.26.0 | Image transforms |
| `facenet-pytorch` | 2.6.0 | FaceNet model & MTCNN |
| `opencv-python` | ≥ 4.13.0 | Camera capture & image processing |
| `mediapipe` | ≥ 0.10.35 | Face detection & 478-pt landmarks |
| `numpy` | ≥ 2.4.0 | Numerical operations |
| `Pillow` | ≥ 12.0 | Image handling for Tkinter |
| `openpyxl` | ≥ 3.1.0 | Excel attendance report generation |
| `requests` | latest | HTTP utilities |
| `tqdm` | latest | Progress bars |

---

## 🧪 Testing

Run the headless test suite (no display required):

```bash
.venv314\Scripts\python.exe tests_headless.py
```

---

## 📋 Attendance Reports

Attendance is automatically saved to `data/attendance/`:

- **`attendance_YYYY-MM-DD.csv`** — Raw comma-separated data
- **`attendance_YYYY-MM-DD.xlsx`** — Styled Excel workbook with frozen header row

Columns: `Date`, `Time`, `Name`, `Confidence`, `Status`

Generate a summary report:

```bash
.venv314\Scripts\python.exe generate_report.py
```

---

## ⚙️ Configuration

Key parameters can be tuned directly in the source files:

| Parameter | File | Default | Description |
|---|---|---|---|
| `EAR_THRESHOLD` | `core/liveness.py` | `0.21` | Eye closure threshold for blink |
| `REQUIRED_BLINKS` | `core/liveness.py` | `2` | Blinks needed to pass liveness |
| `TIMEOUT_SECONDS` | `core/liveness.py` | `8.0` | Time window for liveness check |
| `COOLDOWN_SECONDS` | `core/attendance.py` | `60` | Min seconds between attendance logs |
| `detection_confidence` | `core/detector.py` | `0.5` | Face detection confidence threshold |

---

## 🔧 Troubleshooting

**Tkinter fails to start on Python 3.14 (Windows)**
> The `run.bat` launcher automatically sets `TCL_LIBRARY` and `TK_LIBRARY` environment variables. If running `main.py` directly, use the batch file or set these variables manually.

**Camera not detected**
> Ensure no other application is using the webcam. Try changing the camera index in `core/camera.py`.

**Model download fails**
> Check your internet connection. Models are cached in `core/_models/` after the first download. You can also manually download:
> - [BlazeFace](https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/latest/blaze_face_short_range.tflite)
> - [FaceLandmarker](https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task)

**Low recognition accuracy**
> Register multiple captures per person (5–10 recommended) with varied lighting and angles.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [FaceNet-PyTorch](https://github.com/timesler/facenet-pytorch) by Tim Esler
- [MediaPipe](https://mediapipe.dev/) by Google
- [Soukupová & Čech (2016)](http://vision.fe.uni-lj.si/cvww2016/proceedings/papers/05.pdf) — Real-Time Eye Blink Detection using Facial Landmarks

---

<div align="center">
Made with ❤️ by Harsh &nbsp;|&nbsp; <i>Jagte Raho — Stay Vigilant</i>
</div>
