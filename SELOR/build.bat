@echo off
REM ============================================================
REM  SELOR - build script
REM  Produces a single SELOR.exe in the dist/ folder.
REM ============================================================

echo.
echo  ===  SELOR Build  ===
echo.

REM -- Check that PyInstaller is available (use python -m to avoid PATH issues) --
python -m PyInstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller not found. Install it first:
    echo     pip install pyinstaller
    echo.
    pause
    exit /b 1
)

REM -- Convert logo.png to logo.ico if needed --
if not exist assets\logo.ico (
    echo Converting logo.png to logo.ico ...
    python -c "from PIL import Image; img = Image.open('assets/logo.png'); img.save('assets/logo.ico', format='ICO', sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])"
    if %errorlevel% neq 0 (
        echo [WARNING] Could not convert PNG to ICO. Building without custom icon.
        echo           Install Pillow if you want the icon: pip install Pillow
        echo.
    )
)

REM -- Clean previous build artifacts --
if exist build rd /s /q build
if exist dist  rd /s /q dist

REM -- Build --
if exist assets\logo.ico (
    echo Building with custom icon...
    python -m PyInstaller --noconfirm --onefile --windowed --name SELOR --icon=assets/logo.ico --add-data "assets;assets" app.py
) else (
    echo Building without custom icon...
    python -m PyInstaller --noconfirm --onefile --windowed --name SELOR --add-data "assets;assets" app.py
)

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Build failed. Check the errors above.
    pause
    exit /b 1
)

echo.
echo  ===  Build complete!  ===
echo  Output: dist\SELOR.exe
echo.
pause
