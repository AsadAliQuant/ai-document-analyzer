@echo off
setlocal EnableExtensions EnableDelayedExpansion

pushd "%~dp0"
set APP_NAME=AI Document Analyzer Debug
set DIST_DIR=dist
set BUILD_DIR=build
set "PYEXE=.venv311\Scripts\python.exe"

if not exist "%PYEXE%" (
    echo ERROR: Python 3.11 virtual environment not found at .venv311
    popd
    pause
    exit /b 1
)

echo ============================================================
echo DEBUG BUILD - Using Python: %PYEXE%
echo ============================================================

echo.
echo [1/3] Installing dependencies...
"%PYEXE%" -m pip install pyinstaller
"%PYEXE%" -m pip install -r requirements.txt

echo.
echo [2/3] Cleaning previous debug build...
if exist "%DIST_DIR%\%APP_NAME%.exe" del /F /Q "%DIST_DIR%\%APP_NAME%.exe"

echo.
echo [3/3] Building DEBUG executable with console window...
REM Retained dependencies expose optional sentence-transformers/Transformers integrations.
"%PYEXE%" -m PyInstaller --noconfirm --clean ^
    --name "%APP_NAME%" ^
    --onefile ^
    --console ^
    --paths=. ^
    --add-data "assets;assets" ^
    --add-data "styles.qss;." ^
    --add-data "config.json;." ^
    --add-data "prompts.txt;." ^
    --collect-all=langchain_text_splitters ^
    --collect-all=langchain_core ^
    --collect-all=qdrant_client ^
    --collect-all=google.genai ^
    --collect-all=keyring ^
    --hidden-import=google.genai ^
    --hidden-import=google.genai.types ^
    --hidden-import=gemini_fallback ^
    --hidden-import=qdrant_client.local ^
    --hidden-import=portalocker ^
    --exclude-module=sentence_transformers ^
    --exclude-module=transformers ^
    main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo BUILD FAILED!
    popd
    pause
    exit /b 1
)

echo.
echo ============================================================
echo DEBUG BUILD SUCCESSFUL!
echo ============================================================
echo Debug EXE created at: %CD%\%DIST_DIR%\%APP_NAME%.exe

popd
endlocal
pause
exit /b 0
