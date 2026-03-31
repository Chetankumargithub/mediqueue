# Your Dataset Configuration - ACTIVE

## ✅ What Was Changed

Your MediQueue project is now configured to use your realistic patient dataset **exclusively**.

---

## 📊 Dataset Details

**File Path:** 
```
C:\Users\Sumit and Chetan\Downloads\patient_data_realistic.csv
```

**Status:** ✅ ACTIVE (Primary)

**Generated Data:** ❌ DISABLED

---

## 🔧 Configuration Applied

### app.py Changes:
```python
# Now uses your realistic dataset
CSV_FILE = r"C:\Users\Sumit and Chetan\Downloads\patient_data_realistic.csv"
```

### Behavior:
- ✅ Startup: Loads from YOUR CSV file
- ✅ API: Uses your patient data
- ✅ Reset Button: Reloads your CSV file
- ✅ Export: Exports your data to CSV
- ❌ No more random generated data

---

## 🚀 How to Run

**Start MediQueue with your dataset:**

```powershell
cd "c:\Users\Sumit and Chetan\OneDrive\Desktop\Mediqueue"
python app.py
```

**Expected output:**
```
Dataset configured: C:\Users\Sumit and Chetan\Downloads\patient_data_realistic.csv
Loading patient data from: C:\Users\Sumit and Chetan\Downloads\patient_data_realistic.csv
Loaded [X] patients from patient_data_realistic.csv
```

**Then open browser:**
```
http://localhost:5000
```

---

## ✅ Verification Checklist

- [ ] Server starts without errors
- [ ] Shows "Loaded [X] patients" message
- [ ] Dashboard displays your patients
- [ ] Priority queue shows your data
- [ ] Reset button reloads your dataset
- [ ] Charts show your data distribution
- [ ] Export CSV contains your patients

---

## 📝 Your Dataset CSV Format

Your `patient_data_realistic.csv` should have:

```csv
patient_id,age,heart_rate,oxygen_sat,pain_level,arrival_time
```

**Example:**
```csv
P001,45,85,95,3,08:15
P002,72,120,88,7,08:20
P003,28,90,98,2,08:25
```

---

## 🔄 If File Not Found

If you see error on startup:
```
ERROR: Primary dataset file not found
```

**Solutions:**
1. Ensure file exists at: `C:\Users\Sumit and Chetan\Downloads\patient_data_realistic.csv`
2. Check filename is exactly: `patient_data_realistic.csv`
3. If path changed, update `CSV_FILE` in `app.py`

---

## 🎛️ Change Dataset Path

If you later move your CSV file or want to use a different one:

### Edit app.py:
```python
# Change this line to your new path:
CSV_FILE = r"C:\New\Path\To\your_data.csv"
```

Then restart the server.

---

## 📊 Understanding Your Data

Once loaded, your dataset will:
- ✅ Have acuity scores calculated automatically (0-100)
- ✅ Be sorted by priority (highest score first)
- ✅ Show priority levels (Critical/Moderate/Stable)
- ✅ Support live re-triage (update vitals)
- ✅ Support wait-time boost (+15 points)

---

## 🎯 Features with Your Dataset

| Feature | Works |
|---------|-------|
| Dashboard display | ✅ Yes |
| Priority queue | ✅ Yes |
| Re-triage (update vitals) | ✅ Yes |
| Wait boost | ✅ Yes |
| CSV export | ✅ Yes |
| Reset | ✅ Yes (reloads your data) |
| Charts | ✅ Yes |
| Search/filter | ✅ Yes |

---

## 🔍 Quick Status Check

**Current Configuration:**
- Primary Dataset: `patient_data_realistic.csv`
- Location: `C:\Users\Sumit and Chetan\Downloads\`
- Status: ✅ Active
- Generated Data: ❌ Disabled

---

## 📝 Notes

- Your dataset is loaded on every server startup
- Reset button in UI reloads your CSV
- No random data generation happens
- All operations work with your real data
- Your data is re-sorted by acuity score

---

## ❓ FAQ

**Q: Will the project still work if I delete the CSV?**
A: No, it will error on startup. Keep the file in Downloads.

**Q: Can I update the CSV while the server is running?**
A: Click Reset button after updating the CSV file.

**Q: How do I go back to generated data?**
A: Edit app.py and set `CSV_FILE = None`

**Q: Can I use a different dataset?**
A: Yes, update the `CSV_FILE` path in app.py

---

## 🎉 Ready to Go!

Your MediQueue is now configured to use your realistic patient dataset.

```powershell
python app.py
```

Visit: http://localhost:5000

---

**Configuration Date:** March 18, 2026
**Status:** ✅ Active
**Dataset:** Realistic (patient_data_realistic.csv)
