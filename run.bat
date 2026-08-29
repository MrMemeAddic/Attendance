@echo off
echo ============================================
echo   Jagte Raho -- Face Recognition App Launcher
echo ============================================

REM Check that the venv exists
if not exist ".venv314\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    echo Run: py -3.14 -m venv .venv314
    echo Then install PyTorch: .venv314\Scripts\pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    echo Then install rest:    .venv314\Scripts\pip install facenet-pytorch --no-deps ^& .venv314\Scripts\pip install opencv-python mediapipe requests tqdm pillow
    pause
    exit /b 1
)

REM --- Fix Tcl/Tk paths so Tkinter works on Python 3.14 ---
REM Python 3.14 on Windows does not set TCL_LIBRARY / TK_LIBRARY automatically.
REM We let Python itself locate the correct tcl folder and export it to the env.
for /f "usebackq delims=" %%A in (`".venv314\Scripts\python.exe" -c "import sys,os; candidates=[os.path.join(d,'tcl','tcl8.6') for d in [sys.base_prefix,os.path.join(os.environ.get('LOCALAPPDATA',''),'Programs','Python','Python314')]]; found=next((c for c in candidates if os.path.isfile(os.path.join(c,'init.tcl'))),None); print(found or '')"`) do set _TCL_DIR=%%A

if not "%_TCL_DIR%"=="" (
    set TCL_LIBRARY=%_TCL_DIR%
    for %%D in ("%_TCL_DIR%") do set TK_LIBRARY=%%~dpDtk8.6
)

echo Starting Jagte Raho...
.venv314\Scripts\python.exe main.py
pause
