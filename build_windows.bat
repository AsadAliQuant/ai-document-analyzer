@echo off
echo Building Windows Desktop Application...
echo.

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo Installing/Updating dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo Building executable with PyInstaller...
pyinstaller "AI Document Analyzer.spec"

echo.
echo Build complete! Check the 'dist' folder for your executable.
echo.
pause
