@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM Change to the directory of this script
pushd "%~dp0"

REM ------------------------------------------------------------
REM Settings
REM ------------------------------------------------------------
set APP_NAME=AI Document Analyzer
set ENTRY=main.py
set DIST_DIR=dist
set BUILD_DIR=build
set SPEC_FILE=%APP_NAME%.spec

REM Optional icon
set ICON_OPT=
if exist assets\logo.ico (
  set ICON_OPT=--icon "assets\logo.ico"
)

REM Pick Python interpreter (prefer local venv)
set "PYEXE=python"
if exist ".venv\Scripts\python.exe" (
  set "PYEXE=.venv\Scripts\python.exe"
)
echo Using Python: %PYEXE%

REM ------------------------------------------------------------
REM Ensure PyInstaller is available
REM ------------------------------------------------------------
"%PYEXE%" -c "import PyInstaller" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
  echo Installing PyInstaller into the selected Python environment...
  "%PYEXE%" -m pip install --upgrade pip >nul 2>&1
  "%PYEXE%" -m pip install --upgrade pyinstaller
  "%PYEXE%" -c "import PyInstaller" >nul 2>&1
  if %ERRORLEVEL% NEQ 0 (
    echo Failed to install PyInstaller. Aborting.
    popd
    pause
    exit /b 1
  ) else (
    echo PyInstaller is ready.
  )
) else (
  echo PyInstaller is ready.
)

REM ------------------------------------------------------------
REM Clean previous builds
REM ------------------------------------------------------------
echo Cleaning previous build artifacts...
if exist "%DIST_DIR%" rmdir /S /Q "%DIST_DIR%"
if exist "%BUILD_DIR%" rmdir /S /Q "%BUILD_DIR%"
if exist "%SPEC_FILE%" del /Q "%SPEC_FILE%"

REM ------------------------------------------------------------
REM Build (ONEDIR for reliability and faster startup)
REM ------------------------------------------------------------
echo Building %APP_NAME% executable...
"%PYEXE%" -m PyInstaller --noconfirm --clean --onedir ^
  --name "%APP_NAME%" ^
  %ICON_OPT% ^
  --add-data "assets;assets" ^
  --add-data "styles.qss;." ^
  --add-data "config.json;." ^
  --collect-all PyQt6 ^
  --collect-all sentence_transformers ^
  --collect-all transformers ^
  --collect-all huggingface_hub ^
  --collect-all google.generativeai ^
  --collect-all numpy ^
  --collect-all torch ^
  --collect-all chromadb ^
  --collect-all easyocr ^
  --collect-all PIL ^
  --collect-submodules langchain_community.vectorstores ^
  --collect-submodules langchain_huggingface ^
  --hidden-import chromadb ^
  --hidden-import chromadb.api ^
  --hidden-import chromadb.config ^
  --hidden-import sqlite3 ^
  --hidden-import easyocr ^
  --hidden-import easyocr.recognition ^
  --hidden-import easyocr.detection ^
  --hidden-import PIL ^
  --hidden-import PIL.Image ^
  --hidden-import cv2 ^
  --hidden-import docx ^
  --hidden-import pkg_resources ^
  "%ENTRY%"

if %ERRORLEVEL% NEQ 0 (
  echo Build failed.
  popd
  exit /b 1
)

echo.
echo Build complete.
echo Run the app here:
echo   %DIST_DIR%\%APP_NAME%\%APP_NAME%.exe
echo.
echo To move to another Windows PC, copy the entire folder:
echo   %DIST_DIR%\%APP_NAME%\

popd
endlocal
if /I "%~1"=="/nopause" (
  exit /b 0
) else (
  echo.
  pause
  exit /b 0
)
