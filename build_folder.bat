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

echo [1/4] Verifying Python 3.11...
"%PYTHON%" -c "import sys; print(sys.executable); print(sys.version); raise SystemExit(0 if sys.version_info[:2] == (3, 11) else 1)"
if errorlevel 1 (
    echo ERROR: The canonical build requires CPython 3.11.
    popd
    pause
    exit /b 1
)

echo [2/4] Verifying PyInstaller 6.17.0 and runtime imports...
"%PYTHON%" -c "import PyInstaller; raise SystemExit(0 if PyInstaller.__version__ == '6.17.0' else 1)"
if errorlevel 1 (
    echo ERROR: PyInstaller 6.17.0 is required.
    echo Install it with: .venv311\Scripts\python.exe -m pip install PyInstaller==6.17.0
    popd
    pause
    exit /b 1
)
"%PYTHON%" -c "import PyQt6, PyPDF2, docx, google.genai, langchain_core, langchain_text_splitters, numpy, qdrant_client, portalocker, requests, cryptography, keyring; import auth, gemini_fallback, gemini_gateway, gemini_ocr, large_doc_manager, startup_helper, main_window, main"
if errorlevel 1 (
    echo ERROR: A required build or runtime import failed.
    popd
    pause
    exit /b 1
)

echo [3/4] Cleaning previous folder build...
if exist "dist\AI Document Analyzer" rmdir /s /q "dist\AI Document Analyzer"
if errorlevel 1 (
    echo ERROR: Could not clean dist\AI Document Analyzer.
    popd
    pause
    exit /b 1
)
if exist "build\app_folder" rmdir /s /q "build\app_folder"
if errorlevel 1 (
    echo ERROR: Could not clean build\app_folder.
    popd
    pause
    exit /b 1
)

echo [4/4] Building application...
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
