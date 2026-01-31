@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo  AI Document Analyzer - Folder Build
echo ============================================================
echo.
echo This creates a FOLDER distribution (more reliable than single EXE)
echo The result will be in: dist\AI Document Analyzer\
echo.

REM Use virtual environment Python
set PYTHON=.venv\Scripts\python.exe
if not exist "%PYTHON%" (
    echo ERROR: Virtual environment not found. Run: python -m venv .venv
    pause
    exit /b 1
)

echo Using Python: %PYTHON%
echo.

REM Check PyInstaller
echo [1/3] Checking PyInstaller...
%PYTHON% -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    .venv\Scripts\pip install pyinstaller
)

REM Clean previous build
echo [2/3] Cleaning previous build...
if exist "dist\AI Document Analyzer" rmdir /s /q "dist\AI Document Analyzer"
if exist "build\AI Document Analyzer" rmdir /s /q "build\AI Document Analyzer"

REM Build
echo [3/3] Building application (folder mode)...
echo This may take several minutes...
echo.

.venv\Scripts\pyinstaller app_folder.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ============================================================
    echo BUILD FAILED
    echo ============================================================
    pause
    exit /b 1
)

echo.
echo ============================================================
echo BUILD SUCCESSFUL
echo ============================================================
echo.
echo Output folder: dist\AI Document Analyzer\
echo.
echo To run: dist\AI Document Analyzer\AI Document Analyzer.exe
echo.
echo To distribute: Zip the entire "dist\AI Document Analyzer" folder
echo and share the ZIP file with users.
echo ============================================================
pause
