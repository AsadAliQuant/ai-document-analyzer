@echo off
echo ========================================
echo AI Document Analyzer - Complete Build
echo ========================================
echo.

REM Check if NSIS is installed
where makensis >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: NSIS not found. Installer will not be created.
    echo Download NSIS from: https://nsis.sourceforge.io/
    echo.
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.exe" del /q "*.exe"

REM Install dependencies
echo Installing/Updating dependencies...
pip install -r requirements.txt
pip install pyinstaller

REM Build the application
echo.
echo Building application executable...
pyinstaller "AI Document Analyzer.spec"

REM Check if build was successful
if not exist "dist\AI Document Analyzer.exe" (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo Application built successfully!

REM Create installer if NSIS is available
where makensis >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Creating Windows installer...
    makensis installer.nsi
    if exist "AI_Document_Analyzer_Setup.exe" (
        echo Installer created: AI_Document_Analyzer_Setup.exe
    ) else (
        echo WARNING: Installer creation failed
    )
) else (
    echo.
    echo Skipping installer creation (NSIS not found)
    echo Your executable is ready at: dist\AI Document Analyzer.exe
)

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Files created:
if exist "dist\AI Document Analyzer.exe" echo - dist\AI Document Analyzer.exe
if exist "AI_Document_Analyzer_Setup.exe" echo - AI_Document_Analyzer_Setup.exe
echo.
pause
