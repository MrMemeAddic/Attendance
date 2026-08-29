# -*- mode: python ; coding: utf-8 -*-
"""
jagte_raho.spec  — PyInstaller spec for Jagte Raho
Bundles: main.py + core/ + ui/ + MediaPipe TFLite models
FaceNet weights are fetched at runtime (cached in ~\.cache\torch\)
"""

import sys, os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

# ── Data files to bundle ──────────────────────────────────────────────────────

datas = []

# MediaPipe TFLite models (already downloaded into core/_models/)
datas += [
    (os.path.join("core", "_models", "blaze_face_short_range.tflite"),
     os.path.join("core", "_models")),
    (os.path.join("core", "_models", "face_landmarker.task"),
     os.path.join("core", "_models")),
]

# MediaPipe package data (internal proto/resource files)
datas += collect_data_files("mediapipe")

# facenet_pytorch package data (model config, etc.)
datas += collect_data_files("facenet_pytorch")

# torchvision package data
datas += collect_data_files("torchvision")

# matplotlib data (fonts, styles — needed by mediapipe drawing_utils)
datas += collect_data_files("matplotlib")

# ── Hidden imports ────────────────────────────────────────────────────────────

hiddenimports = [
    # Tkinter
    "tkinter",
    "tkinter.ttk",
    "tkinter.messagebox",
    "tkinter.filedialog",
    # PIL / Pillow
    "PIL",
    "PIL._tkinter_finder",
    # OpenCV
    "cv2",
    # MediaPipe
    "mediapipe",
    "mediapipe.tasks",
    "mediapipe.tasks.python",
    "mediapipe.tasks.python.vision",
    "mediapipe.tasks.python.components",
    "mediapipe.tasks.python.components.containers",
    "mediapipe.tasks.python.components.containers.landmark",
    # PyTorch
    "torch",
    "torch.nn",
    "torch.nn.functional",
    "torchvision",
    "torchvision.transforms",
    # facenet_pytorch
    "facenet_pytorch",
    # Standard lib
    "sqlite3",
    "threading",
    "csv",
    "logging",
    "queue",
    # openpyxl
    "openpyxl",
    "openpyxl.styles",
    # matplotlib (required by mediapipe drawing_utils)
    "matplotlib",
    "matplotlib.pyplot",
    "matplotlib.backends",
    "matplotlib.backends.backend_agg",
    # Project modules
    "core",
    "core.database",
    "core.embedder",
    "core.matcher",
    "core.detector",
    "core.liveness",
    "core.tracker",
    "core.attendance",
    "core.camera",
    "ui",
    "ui.register_panel",
    "ui.recognize_panel",
    "ui.manage_panel",
]

# ── Binary dependencies ───────────────────────────────────────────────────────

binaries = []
binaries += collect_dynamic_libs("cv2")
binaries += collect_dynamic_libs("mediapipe")

# ── Analysis ──────────────────────────────────────────────────────────────────

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unused large packages to keep size down
        "scipy",
        "pandas",
        "IPython",
        "jupyter",
        "notebook",
        "pytest",
        "setuptools",
        "pkg_resources",
        "_pytest",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── EXE ───────────────────────────────────────────────────────────────────────

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,       # Use COLLECT (folder dist) for easier distribution
    name="JagteRaho",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                    # Compress if UPX is available
    console=False,               # No black console window (windowed app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="logo.ico",             # Jagte Raho app icon
)

# ── COLLECT (folder-based distribution) ──────────────────────────────────────

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="JagteRaho",
)
