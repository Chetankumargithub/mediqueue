@echo off
REM Test MediQueue with sample dataset
REM Run this script to test loading the sample CSV dataset

echo.
echo ====================================================
echo  MediQueue - Dataset Integration Test
echo ====================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/4] Activating virtual environment...
call .venv\Scripts\activate.bat 2>nul
if errorlevel 1 (
    echo ERROR: Virtual environment not found
    pause
    exit /b 1
)

REM Check if sample CSV exists
if not exist sample_patient_data.csv (
    echo ERROR: sample_patient_data.csv not found
    echo Please ensure you are in the Mediqueue project directory
    pause
    exit /b 1
)

REM Set environment variable
echo [2/4] Setting dataset path...
set PATIENT_CSV=sample_patient_data.csv
echo Dataset: %PATIENT_CSV%

REM Start Flask server
echo [3/4] Starting MediQueue server...
echo.
echo ====================================================
echo Server starting... Press Ctrl+C to stop
echo http://localhost:5000
echo ====================================================
echo.

python app.py

pause
