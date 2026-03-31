# Dataset Integration Summary

## ✅ What Was Done

Your MediQueue project is now ready to load custom datasets! Here's what was set up:

---

## 🔧 Code Changes

### 1. **triage_engine.py** (Modified)
Added new function:
```python
load_patient_dataset_from_csv(csv_filepath: str) -> list[dict]
```
- Reads CSV files with patient data
- Validates all column names and data types
- Converts values to correct types (int, float, str)
- Falls back to generated data if errors occur
- Automatically sorts patients by arrival time

Modified `run_pipeline()`:
```python
run_pipeline(csv_file: str = None) -> dict
```
- Now accepts optional CSV file path
- Loads from CSV if provided
- Uses generated data if CSV_file is None

### 2. **app.py** (Modified)
Added environment variable support:
```python
CSV_FILE = os.getenv('PATIENT_CSV', None)
```
- Checks for `PATIENT_CSV` environment variable on startup
- Validates CSV file exists before loading
- Falls back gracefully to generated data

---

## 📁 New Files Created

### Documentation
1. **DATASET_INTEGRATION.md** - Complete integration guide (2000+ words)
   - 3 methods to load datasets
   - Sample datasets
   - Troubleshooting
   - Advanced usage

2. **QUICK_START_DATASET.md** - Quick reference guide
   - Copy & paste examples
   - CSV format requirements
   - Common use cases

### Sample Data
3. **sample_patient_data.csv** - Example dataset with 30 patients
   - Ready to use for testing
   - Properly formatted
   - Includes realistic medical data

### Automation Scripts
4. **run_with_dataset.bat** - Windows batch script
   - Auto-sets environment variable
   - Activates virtual environment
   - Starts Flask server
   - Double-click to run!

5. **run_with_dataset.ps1** - PowerShell script
   - Same functionality as .bat file
   - Better for PowerShell users
   - Pretty colored output

---

## 🚀 How to Use It

### **Method 1: Using the Quick Scripts (Easiest)**

**Windows:**
```
Double-click: run_with_dataset.bat
or
.\run_with_dataset.ps1
```

### **Method 2: Manual with Environment Variable**

**PowerShell:**
```powershell
$env:PATIENT_CSV = "sample_patient_data.csv"
python app.py
```

**Command Prompt:**
```cmd
set PATIENT_CSV=sample_patient_data.csv
python app.py
```

### **Method 3: Programmatic Loading**

```python
from triage_engine import run_pipeline

# Load from CSV
state = run_pipeline(csv_file="my_patients.csv")
```

---

## 📊 CSV Format

### Required Columns
```csv
patient_id,age,heart_rate,oxygen_sat,pain_level,arrival_time
```

### Data Ranges
| Column | Type | Min | Max | Unit |
|--------|------|-----|-----|------|
| patient_id | text | - | - | - |
| age | integer | 0 | 150 | years |
| heart_rate | integer | 30 | 220 | bpm |
| oxygen_sat | integer | 70 | 100 | % |
| pain_level | integer | 1 | 10 | scale |
| arrival_time | text | 00:00 | 23:59 | HH:MM |

### Example
```csv
patient_id,age,heart_rate,oxygen_sat,pain_level,arrival_time
P001,45,85,95,3,08:15
P002,72,120,88,7,08:20
P003,28,90,98,2,08:25
```

---

## ✨ Features

✅ **Multiple Loading Methods**
- Environment variables
- Programmatic API
- Hardcoded paths

✅ **Automatic Validation**
- Column name checking
- Data type conversion
- Range validation

✅ **Graceful Fallback**
- CSV loads successfully → Use it
- CSV errors → Use generated data (210 patients)
- Continue operation without crashes

✅ **Easy Switching**
- Change dataset just by changing environment variable
- Restart server to switch
- Reset button in UI reloads dataset

✅ **Well Documented**
- 2 complete guides included
- Sample data provided
- Automation scripts ready

---

## 📋 Checklist: Getting Started

- [ ] Create your CSV file with patient data
- [ ] Place CSV in Mediqueue project folder
- [ ] Run with: `$env:PATIENT_CSV = "your_file.csv"; python app.py`
- [ ] Open: http://localhost:5000
- [ ] Verify data in priority queue table
- [ ] Try re-triaging patients
- [ ] Export as CSV
- [ ] Done! 🎉

---

## 🎯 Quick Testing

### Test 1: Load Sample Data
```powershell
$env:PATIENT_CSV = "sample_patient_data.csv"
python app.py
# Visit http://localhost:5000
# Should see 30 patients from sample data
```

### Test 2: Switch to Generated Data
```powershell
# Restart server without PATIENT_CSV
python app.py
# Should see 210 randomly generated patients
```

### Test 3: Use Your Data
```powershell
# Create your_data.csv
$env:PATIENT_CSV = "your_data.csv"
python app.py
```

---

## 🔗 How It Works

```
User Action
    ↓
app.py checks PATIENT_CSV environment variable
    ↓
run_pipeline(csv_file=...) called
    ↓
triage_engine.py loads CSV or generates data
    ↓
Patients processed through triage algorithm
    ↓
Priority queue created (sorted by acuity score)
    ↓
Data returned to Flask API
    ↓
UI displays in priority queue table
```

---

## 💾 Files Modified/Created

### Modified Files
```
triage_engine.py      ← Added load_patient_dataset_from_csv()
app.py               ← Added CSV_FILE environment variable
```

### Created Files
```
DATASET_INTEGRATION.md          ← Full guide (2000+ words)
QUICK_START_DATASET.md         ← Quick reference
sample_patient_data.csv        ← Example dataset (30 patients)
run_with_dataset.bat           ← Windows batch launcher
run_with_dataset.ps1           ← PowerShell launcher
THIS FILE (Summary)
```

---

## 🎁 Bonus: Python Data Generator

Need to create test data? Copy this:

```python
import csv
import random
from datetime import datetime, timedelta

# Generate test patients
base_time = datetime.now().replace(hour=8, minute=0)

with open('test_data.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['patient_id','age','heart_rate','oxygen_sat','pain_level','arrival_time'])
    writer.writeheader()
    
    for i in range(1, 101):
        arrival = base_time + timedelta(minutes=i*5)
        writer.writerow({
            'patient_id': f'TEST{i:03d}',
            'age': random.randint(18, 85),
            'heart_rate': random.randint(60, 140),
            'oxygen_sat': random.randint(85, 100),
            'pain_level': random.randint(1, 10),
            'arrival_time': arrival.strftime('%H:%M')
        })

print("Created test_data.csv with 100 patients")
```

---

## 🆘 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| "CSV file not found" | Place CSV in project root (same folder as app.py) |
| "ERROR loading CSV" | Check column names and data format |
| Wrong number of patients | System loaded CSV or fell back to generated data |
| Scores look wrong | Verify vitals are in correct ranges |

---

## 📚 Documentation Structure

```
Mediqueue/
├── README.md                    ← Project overview
├── TEST_REPORT.md              ← Test results
├── DATASET_INTEGRATION.md       ← Detailed guide (THIS)
├── QUICK_START_DATASET.md       ← Quick reference
├── SETUP_INSTRUCTIONS.txt       ← (If exists)
└── (Source code files)
```

---

## ✅ You're All Set!

Your MediQueue project can now:
- ✅ Load custom patient datasets from CSV files
- ✅ Switch between datasets easily
- ✅ Fall back gracefully to generated data if needed
- ✅ Process any dataset through the triage algorithm
- ✅ Export results back to CSV

**Next Step:**
1. Create your CSV file with patient data
2. Run with: `$env:PATIENT_CSV = "your_file.csv"; python app.py`
3. Open http://localhost:5000
4. Enjoy your custom dataset in MediQueue! 🏥

---

**For detailed help, see:**
- **DATASET_INTEGRATION.md** - Complete guide
- **QUICK_START_DATASET.md** - Quick reference
- **sample_patient_data.csv** - Example to copy from

**Questions?** Check the troubleshooting section in DATASET_INTEGRATION.md

---

**Last Updated:** March 18, 2026
**Status:** ✅ Ready for use
**Dataset Support:** Fully functional
