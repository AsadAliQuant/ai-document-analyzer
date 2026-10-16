@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ============================================================
REM AI Document Analyzer - DEBUG Build Script
REM Creates EXE with console window to see errors
REM ============================================================

pushd "%~dp0"

set APP_NAME=AI Document Analyzer Debug
set DIST_DIR=dist
set BUILD_DIR=build

REM Pick Python interpreter (prefer local venv)
set "PYEXE=python"
if exist ".venv\Scripts\python.exe" (
    set "PYEXE=.venv\Scripts\python.exe"
)
echo ============================================================
echo DEBUG BUILD - Using Python: %PYEXE%
echo ============================================================

REM Install dependencies
echo.
echo [1/4] Installing dependencies...
"%PYEXE%" -m pip install --upgrade pip >nul 2>&1
"%PYEXE%" -m pip install pyinstaller >nul 2>&1
"%PYEXE%" -m pip install -r requirements.txt --quiet

REM Clean previous builds
echo.
echo [2/4] Cleaning previous build artifacts...
if exist "%DIST_DIR%\%APP_NAME%.exe" del /F /Q "%DIST_DIR%\%APP_NAME%.exe"

REM Prefetch EasyOCR weights
echo.
echo [3/4] Checking offline OCR models...
if exist "offline_bootstrap.py" (
    echo Prefetching missing OCR models...
    "%PYEXE%" offline_bootstrap.py --prefetch --target models
)

REM Build with console enabled for debugging
echo.
echo [4/4] Building DEBUG executable with console window...
echo This will show all errors when running the EXE.
echo.

"%PYEXE%" -m PyInstaller --noconfirm --clean ^
    --name "AI Document Analyzer Debug" ^
    --onefile ^
    --console ^
    --paths=. ^
    --add-data "assets;assets" ^
    --add-data "styles.qss;." ^
    --add-data "config.json;." ^
    --add-data "prompts.txt;." ^
    --hidden-import=langchain_text_splitters ^
    --hidden-import=langchain_text_splitters.character ^
    --hidden-import=langchain_text_splitters.base ^
    --hidden-import=langchain_core ^
    --hidden-import=langchain_core.documents ^
    --hidden-import=easyocr ^
    --hidden-import=easyocr.easyocr ^
    --hidden-import=easyocr.recognition ^
    --hidden-import=easyocr.detection ^
    --hidden-import=google.genai ^
    --hidden-import=skimage ^
    --hidden-import=skimage.transform ^
    --hidden-import=imageio ^
    --hidden-import=scipy.ndimage ^
    --hidden-import=cv2 ^
    --collect-all=easyocr ^
    --collect-all=langchain_text_splitters ^
    --collect-all=langchain_core ^
    --collect-all=google.genai ^
    --collect-all=skimage ^
    --collect-all=imageio ^
    --additional-hooks-dir=hooks ^
    --runtime-hook=hooks/rthook_imports.py ^
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
echo.
echo Debug EXE created at: %CD%\%DIST_DIR%\AI Document Analyzer Debug.exe
echo.
echo Run this EXE from command prompt to see all errors:
echo   cd "%CD%\%DIST_DIR%"
echo   "AI Document Analyzer Debug.exe"
echo.
echo The console window will show any import errors or exceptions.
echo ============================================================

popd
endlocal
pause
exit /b 0
