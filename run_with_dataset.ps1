# Test MediQueue with sample dataset
# Run this script to test loading the sample CSV dataset

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " MediQueue - Dataset Integration Test" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    python --version 2>$null | Out-Null
} catch {
    Write-Host "ERROR: Python not found. Please install Python 3.10+" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if sample CSV exists
if (-not (Test-Path "sample_patient_data.csv")) {
    Write-Host "ERROR: sample_patient_data.csv not found" -ForegroundColor Red
    Write-Host "Please ensure you are in the Mediqueue project directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "[1/4] Activating virtual environment..." -ForegroundColor Green
& .\.venv\Scripts\Activate.ps1

# Set environment variable
Write-Host "[2/4] Setting dataset path..." -ForegroundColor Green
$env:PATIENT_CSV = "sample_patient_data.csv"
Write-Host "Dataset: $env:PATIENT_CSV" -ForegroundColor Yellow

# Start Flask server
Write-Host "[3/4] Starting MediQueue server..." -ForegroundColor Green
Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "Server starting... Press Ctrl+C to stop" -ForegroundColor Cyan
Write-Host "http://localhost:5000" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

python app.py

Read-Host "Press Enter to exit"
