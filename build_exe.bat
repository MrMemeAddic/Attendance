@echo off
setlocal
echo ============================================================
echo   Jagte Raho -- EXE Builder
echo ============================================================

REM ── Check venv ────────────────────────────────────────────────
if not exist ".venv314\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    echo Run INSTALL.md steps first to create .venv314
    pause & exit /b 1
)

REM ── Install PyInstaller into venv ──────────────────────────────
echo [1/3] Installing PyInstaller...
.venv314\Scripts\pip install pyinstaller --quiet
if errorlevel 1 ( echo [ERROR] PyInstaller install failed & pause & exit /b 1 )

REM ── Clean old build artefacts ─────────────────────────────────
echo [2/3] Cleaning old build...
if exist "dist\JagteRaho" rmdir /s /q "dist\JagteRaho"
if exist "build\JagteRaho" rmdir /s /q "build\JagteRaho"

REM ── Run PyInstaller with the spec file ────────────────────────
echo [3/3] Building EXE (this may take 5-15 minutes)...
.venv314\Scripts\pyinstaller jagte_raho.spec --noconfirm --clean

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed. Check the output above for details.
    pause & exit /b 1
)

echo.
echo ============================================================
echo   BUILD COMPLETE
echo   Output folder: dist\JagteRaho\
echo   Executable   : dist\JagteRaho\JagteRaho.exe
echo ============================================================
echo.
echo You can now zip "dist\JagteRaho\" and distribute it.
pause
