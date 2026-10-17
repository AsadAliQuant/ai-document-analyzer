@echo off
setlocal enabledelayedexpansion

pushd "%~dp0"
set "PYTHON=.venv311\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo ERROR: Python 3.11 virtual environment not found at .venv311
    popd
    pause
    exit /b 1
)

echo ============================================================
echo  AI Document Analyzer - Folder Build
echo ============================================================
echo.
echo This creates dist\AI Document Analyzer\
echo Using Python: %PYTHON%
echo.

echo [1/3] Checking PyInstaller...
"%PYTHON%" -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    "%PYTHON%" -m pip install pyinstaller
)

echo [2/3] Cleaning previous folder build...
if exist "dist\AI Document Analyzer" rmdir /s /q "dist\AI Document Analyzer"
if exist "build\AI Document Analyzer" rmdir /s /q "build\AI Document Analyzer"

echo [3/3] Building application...
"%PYTHON%" -m PyInstaller app_folder.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo BUILD FAILED
    popd
    pause
    exit /b 1
)

echo.
echo ============================================================
echo BUILD SUCCESSFUL
echo ============================================================
echo Output folder: dist\AI Document Analyzer\
echo To run: dist\AI Document Analyzer\AI Document Analyzer.exe

popd
endlocal
pause
exit /b 0
