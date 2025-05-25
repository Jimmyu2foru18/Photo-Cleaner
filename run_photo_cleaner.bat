@echo off
REM Photo Cleaner - Windows Batch Script
REM This script provides an easy way to run the Photo Cleaner on Windows

echo ========================================
echo Photo Cleaner - NSFW Detection Tool
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Check if setup has been run
if not exist "test_photos" (
    echo First time setup detected...
    echo Running setup script...
    echo.
    python setup.py
    echo.
)

REM Main menu
:menu
echo.
echo Choose an option:
echo 1. Run Photo Cleaner (Simple Version)
echo 2. Run Photo Cleaner (Advanced Version)
echo 3. Test with sample photos (Dry Run)
echo 4. Install/Update Dependencies
echo 5. View Help
echo 6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto simple
if "%choice%"=="2" goto advanced
if "%choice%"=="3" goto test
if "%choice%"=="4" goto install
if "%choice%"=="5" goto help
if "%choice%"=="6" goto exit

echo Invalid choice. Please try again.
goto menu

:simple
echo.
set /p input_dir="Enter the path to your photos directory: "
if "%input_dir%"=="" (
    echo Error: Please provide a valid directory path.
    goto menu
)
echo.
echo Running Simple Photo Cleaner...
python simple_photo_cleaner.py -i "%input_dir%" -v
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:advanced
echo.
set /p input_dir="Enter the path to your photos directory: "
if "%input_dir%"=="" (
    echo Error: Please provide a valid directory path.
    goto menu
)
echo.
echo Running Advanced Photo Cleaner...
python photo_cleaner.py -i "%input_dir%" -v
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:test
echo.
echo Running test with sample photos (Dry Run)...
if exist "test_photos" (
    python simple_photo_cleaner.py -i "test_photos" --dry-run -v
) else (
    echo Test photos not found. Running setup first...
    python setup.py
    python simple_photo_cleaner.py -i "test_photos" --dry-run -v
)
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:install
echo.
echo Installing/Updating dependencies...
python setup.py
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:help
echo.
echo ========================================
echo Photo Cleaner Help
echo ========================================
echo.
echo This tool scans photos for NSFW content and organizes them
echo into separate folders based on sensitivity thresholds.
echo.
echo Features:
echo - Automatic NSFW detection
echo - Configurable sensitivity thresholds
echo - Batch processing
echo - Safe operation with dry-run mode
echo - Detailed logging and reports
echo.
echo Output Structure:
echo - clean_photos/     : Photos below threshold
echo - sensitive_photos/ : Photos above threshold
echo - photo_cleaner.log : Operation log
echo - scan_report.txt   : Summary report
echo.
echo Manual Usage:
echo python simple_photo_cleaner.py -i "path\to\photos"
echo python photo_cleaner.py -i "path\to\photos" -t 0.7
echo.
echo For more options: python photo_cleaner.py --help
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:exit
echo.
echo Thank you for using Photo Cleaner!
echo.
pause
exit /b 0