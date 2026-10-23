@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo    AI Document Analyzer - EXE Builder (Python 3.11)
echo ============================================================
echo.

cd /d "%~dp0"

set "VENV=.venv311"
set "PYEXE=%CD%\%VENV%\Scripts\python.exe"

REM Check if venv exists
if not exist "%PYEXE%" (
    echo [ERROR] Python 3.11 virtual environment not found!
    echo         Expected: %VENV%
    echo.
    echo Run this first to create it:
    echo   py -3.11 -m venv .venv311
    echo   .venv311\Scripts\python.exe -m pip install -r requirements.txt pyinstaller
    echo.
    pause
    exit /b 1
)

echo [OK] Using Python: %PYEXE%
"%PYEXE%" --version
echo.

REM Verify critical imports before building
echo [1/2] Verifying RAG imports...
"%PYEXE%" -c "from qdrant_client import QdrantClient; from google import genai; print('[OK] All RAG imports working')"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] RAG imports failed!
    echo         Run: %PYEXE% -m pip install -r requirements.txt
    pause
    exit /b 1
)
echo.

REM Build EXE
echo [2/2] Building EXE (this takes 15-25 minutes)...
echo.

REM Retained dependencies expose optional sentence-transformers/Transformers integrations.
"%PYEXE%" -m PyInstaller --noconfirm --onefile --noconsole ^
    --name "AI Document Analyzer" ^
    --icon=assets\logo.ico ^
    --add-data "assets;assets" ^
    --add-data "styles.qss;." ^
    --add-data "config.json;." ^
    --collect-all langchain_text_splitters ^
    --collect-all langchain_core ^
    --collect-all qdrant_client ^
    --collect-all google.genai ^
    --hidden-import google.genai ^
    --hidden-import gemini_fallback ^
    --hidden-import qdrant_client.local ^
    --hidden-import portalocker ^
    --collect-all keyring ^
    --hidden-import keyring ^
    --hidden-import keyring.backends ^
    --exclude-module sentence_transformers ^
    --exclude-module transformers ^
    main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Build failed! Check the output above.
    pause
    exit /b 1
)

REM Verify output
if exist "dist\AI Document Analyzer.exe" (
    echo.
    echo ============================================================
    echo    BUILD SUCCESSFUL!
    echo ============================================================
    echo.
    echo    Executable: dist\AI Document Analyzer.exe
    for %%A in ("dist\AI Document Analyzer.exe") do echo    Size: %%~zA bytes
    echo.
    echo ============================================================
) else (
    echo.
    echo [ERROR] Build completed but EXE not found!
)

pause
exit /b 0
