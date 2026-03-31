# Dataset Integration Guide for MediQueue

## 📁 How to Link a New Dataset File

You have **3 ways** to integrate your own patient dataset into MediQueue:

---

## **Method 1: Using Environment Variable (Recommended)**

### Best for: Quick testing with different datasets

### Step 1: Create your CSV file

Save as `patient_data.csv` (or any filename) in the project root:

```
C:\Users\Sumit and Chetan\OneDrive\Desktop\Mediqueue\patient_data.csv
```

### Step 2: CSV Format

Your CSV must have these columns:

```csv
patient_id,age,heart_rate,oxygen_sat,pain_level,arrival_time
P001,45,85,95,3,08:15
P002,72,120,88,7,08:20
P003,28,90,98,2,08:25
P004,65,140,82,9,08:30
P005,52,95,96,4,08:45
```

**Column Requirements:**
- `patient_id` - Unique identifier (e.g., P001, P002)
- `age` - Integer, 0-100
- `heart_rate` - Integer, 30-200 bpm
- `oxygen_sat` - Integer, 70-100 (percentage)
- `pain_level` - Integer, 1-10
- `arrival_time` - Time in HH:MM format (24-hour)

### Step 3: Run with Dataset

#### Windows PowerShell:
```powershell
cd "c:\Users\Sumit and Chetan\OneDrive\Desktop\Mediqueue"
$env:PATIENT_CSV = "patient_data.csv"
python app.py
```

#### Windows Command Prompt:
```cmd
cd "c:\Users\Sumit and Chetan\OneDrive\Desktop\Mediqueue"
set PATIENT_CSV=patient_data.csv
python app.py
```

#### Linux/Mac:
```bash
cd /path/to/mediqueue
export PATIENT_CSV=patient_data.csv
python app.py
```

### Step 4: Verify

Your browser console will show:
```
Loading patient data from: patient_data.csv
Loaded 5 patients from patient_data.csv
```

---

## **Method 2: Programmatic Loading (For Scripts)**

If you want to load the dataset directly in Python:

```python
from triage_engine import load_patient_dataset_from_csv, run_pipeline

# Option A: Use run_pipeline with CSV
patients = run_pipeline(csv_file="patient_data.csv")

# Option B: Load data directly
patients = load_patient_dataset_from_csv("patient_data.csv")
```

---

## **Method 3: Modify app.py Directly (Hardcoded)**

Edit `app.py` and change line:

```python
CSV_FILE = os.getenv('PATIENT_CSV', None)
```

To:

```python
CSV_FILE = "patient_data.csv"  # Hardcoded path
```

---

## **Sample Datasets**

### Example 1: Hospital Emergency Room Data

```csv
patient_id,age,heart_rate,oxygen_sat,pain_level,arrival_time
ER001,34,88,97,2,08:00
ER002,67,112,91,8,08:05
ER003,45,95,95,3,08:10
ER004,78,125,85,9,08:15
ER005,22,82,99,1,08:20
ER006,55,110,87,7,08:25
ER007,41,98,96,4,08:30
ER008,86,145,80,10,08:35
ER009,29,75,98,2,08:40
ER010,72,135,84,8,08:45
```

### Example 2: Trauma Center Data

```csv
patient_id,age,heart_rate,oxygen_sat,pain_level,arrival_time
TRAUMA001,45,160,75,10,09:00
TRAUMA002,78,150,78,10,09:05
TRAUMA003,34,155,76,9,09:10
TRAUMA004,62,145,80,9,09:15
TRAUMA005,51,140,82,8,09:20
```

---

## **Data Validation**

The system automatically validates your data:

✅ **Automatically Handled:**
- Strips whitespace from text fields
- Converts strings to integers
- Sorts by arrival time
- Adds missing fields (wait_boost = False)
- Falls back to generated data if CSV errors

❌ **Will Cause Errors:**
- Missing columns
- Non-numeric values in numeric fields
- Invalid time format (must be HH:MM)

---

## **Troubleshooting**

### Issue: "CSV file not found"
**Solution:** Make sure your CSV is in the project root:
```
C:\Users\Sumit and Chetan\OneDrive\Desktop\Mediqueue\patient_data.csv
```

### Issue: "ERROR loading CSV"
**Checklist:**
- [ ] Columns are exactly: `patient_id,age,heart_rate,oxygen_sat,pain_level,arrival_time`
- [ ] No empty rows
- [ ] Numbers are valid (age 0-100, HR 30-200, O2 70-100, pain 1-10)
- [ ] Time format is HH:MM (e.g., 08:15, not 8:15 or 8:15 AM)

### Issue: "Falls back to generated data"
**Why:** CSV couldn't be loaded (check above checklist)
**Solution:** Fix the CSV and restart the server

---

## **Create CSV from Excel**

1. Open Excel/LibreOffice
2. Create columns: `patient_id`, `age`, `heart_rate`, `oxygen_sat`, `pain_level`, `arrival_time`
3. Add your data
4. Save As → `patient_data.csv` (CSV format)
5. Place in Mediqueue project root

---

## **Reset to Generated Data**

To go back to random generated data, either:

**Option 1:** Remove environment variable and restart:
```powershell
$env:PATIENT_CSV = ""
python app.py
```

**Option 2:** Delete the CSV file and restart

**Option 3:** Use the Reset button in the UI (↺ Reset)

---

## **Advanced: Load from Different Directory**

Use full path in environment variable:

```powershell
$env:PATIENT_CSV = "C:\path\to\my\patient_data.csv"
python app.py
```

Or in app.py:
```python
CSV_FILE = r"C:\path\to\my\patient_data.csv"
```

---

## **Supported CSV Locations**

✅ Works from:
- Project root folder
- Any subfolder with relative path: `data/patient_data.csv`
- Absolute paths: `C:\Users\....\patient_data.csv`

---

## **API Reset with Dataset**

When you click the **Reset button** in the UI, it:
- Regenerates the dataset (if CSV is loaded, reloads it)
- Recalculates all scores
- Recreates the priority queue
- Updates metrics and charts

---

## **Example Workflow**

1. **Create dataset**:
   ```
   patient_data.csv (210 patients from real hospital data)
   ```

2. **Set environment variable**:
   ```powershell
   $env:PATIENT_CSV = "patient_data.csv"
   ```

3. **Start server**:
   ```
   python app.py
   ```

4. **Open browser**:
   ```
   http://localhost:5000
   ```

5. **See your data** in the priority queue table!

---

## **Quick Reference: CSV Generator**

Need to bulk-create test data? Use this Python script:

```python
import csv
import random

# Generate 50 test patients
with open('test_patients.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['patient_id','age','heart_rate','oxygen_sat','pain_level','arrival_time'])
    writer.writeheader()
    
    for i in range(1, 51):
        hour = 8 + (i // 6)
        minute = 15 * (i % 6)
        time_str = f"{hour:02d}:{minute:02d}"
        
        writer.writerow({
            'patient_id': f'TEST{i:03d}',
            'age': random.randint(18, 85),
            'heart_rate': random.randint(60, 140),
            'oxygen_sat': random.randint(85, 100),
            'pain_level': random.randint(1, 10),
            'arrival_time': time_str
        })

print("Created test_patients.csv with 50 patients")
```

---

## **Summary**

| Method | Ease | Use Case |
|--------|------|----------|
| Environment Variable | Easy | Testing, quick switching |
| Programmatic | Medium | Scripts, automation |
| Hardcoded | Hard | Permanent setup |

**Recommended: Use Environment Variable (Method 1)** for maximum flexibility!

---

**Your MediQueue project is now ready to work with any dataset! 🏥📊**
