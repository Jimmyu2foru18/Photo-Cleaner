@echo off
setlocal enabledelayedexpansion

echo Photo Cleaner GUI Launcher
echo ========================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.7 or higher from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Install GUI-related packages first
echo Installing GUI packages...
python -m pip install --upgrade pip
python -m pip install customtkinter ttkbootstrap tkinter-tooltip

:: Try to install TensorFlow and related packages
echo.
echo Installing TensorFlow and related packages...
echo This may take a few minutes...

python -m pip install tensorflow tensorflow-hub pillow tqdm

:: Check if TensorFlow was installed successfully
python -c "import tensorflow" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: TensorFlow installation failed.
    echo This is likely because:
    echo  1. Your Python version is not compatible with TensorFlow
    echo  2. Your system doesn't meet TensorFlow requirements
    echo.
    echo The GUI will still launch, but scanning functionality may be limited.
    echo You can try installing TensorFlow manually with:
    echo  pip install tensorflow==2.8.0
    echo.
    pause
)

:: Run the GUI application
echo.
echo Starting Photo Cleaner GUI...
echo.
python "%~dp0photo_cleaner_gui.py"

:: Check if the application exited with an error
if %errorlevel% neq 0 (
    echo.
    echo The application encountered an error.
    echo Please check the console output above for details.
    echo.
    echo If you're seeing TensorFlow-related errors, you can try:
    echo  1. Installing an older version: pip install tensorflow==2.8.0
    echo  2. Using the simple version without TensorFlow: python simple_photo_cleaner.py -h
    pause
    exit /b %errorlevel%
)

exit /b 0