@echo off
echo Clearing locked Qdrant vector stores...
echo.

REM Kill any Python processes that might be holding locks
echo Checking for running Python processes...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1

REM Wait a moment for processes to fully terminate
timeout /t 2 /nobreak >nul

REM Delete the vector store folder
echo Deleting vector store folder...
if exist "%APPDATA%\AI Document Analyzer\vector_store" (
    rmdir /S /Q "%APPDATA%\AI Document Analyzer\vector_store"
    if %ERRORLEVEL% EQU 0 (
        echo ✓ Vector store folder cleared successfully!
    ) else (
        echo × Failed to delete folder. It may still be locked.
        echo.
        echo Please try:
        echo 1. Close ALL Python windows/processes
        echo 2. Restart your computer if the issue persists
        echo 3. Manually delete: %APPDATA%\AI Document Analyzer\vector_store
    )
) else (
    echo Folder doesn't exist or already cleared.
)

echo.
echo You can now run the application again.
echo.
pause
