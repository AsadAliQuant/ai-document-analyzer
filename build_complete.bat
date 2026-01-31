@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ============================================================
REM AI Document Analyzer - Build Script
REM Creates a single standalone EXE for Windows 10/11
REM ============================================================

REM Change to the directory of this script
pushd "%~dp0"

REM ------------------------------------------------------------
REM Settings
REM ------------------------------------------------------------
set APP_NAME=AI Document Analyzer
set SPEC_FILE=app.spec
set DIST_DIR=dist
set BUILD_DIR=build

REM Pick Python interpreter (prefer local venv)
set "PYEXE=python"
if exist ".venv\Scripts\python.exe" (
    set "PYEXE=.venv\Scripts\python.exe"
)
echo ============================================================
echo Using Python: %PYEXE%
echo ============================================================

REM ------------------------------------------------------------
REM Ensure all required packages are installed
REM ------------------------------------------------------------
echo.
echo [1/4] Checking and installing required packages...
"%PYEXE%" -m pip install --upgrade pip >nul 2>&1

REM Install PyInstaller if missing
"%PYEXE%" -c "import PyInstaller" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing PyInstaller...
    "%PYEXE%" -m pip install pyinstaller
)

REM Ensure langchain-text-splitters is installed
"%PYEXE%" -c "import langchain_text_splitters" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing langchain-text-splitters...
    "%PYEXE%" -m pip install langchain-text-splitters
)

REM Install all requirements
echo Installing/updating all requirements...
"%PYEXE%" -m pip install -r requirements.txt --quiet

echo PyInstaller and dependencies are ready.

REM ------------------------------------------------------------
REM Clean previous builds
REM ------------------------------------------------------------
echo.
echo [2/4] Cleaning previous build artifacts...
if exist "%DIST_DIR%" rmdir /S /Q "%DIST_DIR%"
if exist "%BUILD_DIR%" rmdir /S /Q "%BUILD_DIR%"

REM ------------------------------------------------------------
REM Prefetch offline models into ./models if missing
REM ------------------------------------------------------------
echo.
echo [3/4] Checking offline models...
set MODELS_OK=0
if exist "models\sentence-transformers\all-MiniLM-L6-v2\config.json" set MODELS_OK=1
if %MODELS_OK%==0 (
    if exist "offline_bootstrap.py" (
        echo Prefetching offline models into .\models ...
        "%PYEXE%" offline_bootstrap.py --prefetch --target models
    ) else (
        echo Note: offline_bootstrap.py not found, skipping model prefetch.
    )
) else (
    echo Offline models already present.
)

REM ------------------------------------------------------------
REM Build using spec file
REM ------------------------------------------------------------
echo.
echo [4/4] Building %APP_NAME% executable...
echo This may take several minutes...
echo.

"%PYEXE%" -m PyInstaller --noconfirm --clean "%SPEC_FILE%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================================
    echo BUILD FAILED!
    echo ============================================================
    echo Check the output above for errors.
    popd
    pause
    exit /b 1
)

echo.
echo ============================================================
echo BUILD SUCCESSFUL!
echo ============================================================
echo.
echo Single-file EXE created:
echo   %CD%\%DIST_DIR%\%APP_NAME%.exe
echo.
echo File size:
for %%A in ("%DIST_DIR%\%APP_NAME%.exe") do echo   %%~zA bytes
echo.
echo You can copy this EXE to any Windows 10/11 PC and run it directly.
echo No Python installation required on the target machine.
echo ============================================================

popd
endlocal

if /I "%~1"=="/nopause" (
    exit /b 0
) else (
    echo.
    pause
    exit /b 0
)
