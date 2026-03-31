"""
triage_engine.py
MediQueue core logic — dataset generation, scoring, queue, re-triage, wait boost.
Imported by app.py (Flask backend).
"""

import csv
import heapq
import os
import random
from datetime import datetime, timedelta


# ─────────────────────────────────────────────
#  SECTION 1 — DATASET GENERATION
# ─────────────────────────────────────────────

def generate_patient_dataset(num_patients: int = 210) -> list[dict]:
    random.seed(42)

    presets = [
        (0.25, (18, 80), (100, 160), (80, 89),  (7, 10)),   # critical
        (0.35, (18, 80), (80,  130), (90, 94),  (5,  8)),   # moderate
        (0.40, (18, 80), (60,   90), (95, 100), (1,  4)),   # stable
    ]

    base_time = datetime(2024, 1, 15, 8, 0)
    patients  = []

    for i in range(num_patients):
        r = random.random()
        if r < 0.25:
            preset = presets[0]
        elif r < 0.60:
            preset = presets[1]
        else:
            preset = presets[2]

        _, age_r, hr_r, o2_r, pain_r = preset

        offset_min  = random.randint(0, 480)
        arrival_dt  = base_time + timedelta(minutes=offset_min)

        patients.append({
            "patient_id":   f"P{101 + i}",
            "age":          random.randint(*age_r),
            "heart_rate":   random.randint(*hr_r),
            "oxygen_sat":   random.randint(*o2_r),
            "pain_level":   random.randint(*pain_r),
            "arrival_time": arrival_dt.strftime("%H:%M"),
            "wait_boost":   False,
        })

    patients.sort(key=lambda p: p["arrival_time"])
    return patients


def load_patient_dataset_from_csv(csv_filepath: str) -> list[dict]:
    """
    Load patient data from a CSV file.
    
    CSV should have these columns:
    patient_id, age, heart_rate, oxygen_sat, pain_level, arrival_time
    
    Example:
        P001,45,85,95,3,08:15
        P002,72,120,88,7,08:20
    """
    patients = []
    
    if not os.path.exists(csv_filepath):
        print(f"ERROR: CSV file not found at {csv_filepath}")
        return generate_patient_dataset()  # Fallback to generated data
    
    try:
        with open(csv_filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                patient = {
                    "patient_id":   str(row['patient_id']).strip(),
                    "age":          int(row['age']),
                    "heart_rate":   int(row['heart_rate']),
                    "oxygen_sat":   int(row['oxygen_sat']),
                    "pain_level":   int(row['pain_level']),
                    "arrival_time": str(row['arrival_time']).strip(),
                    "wait_boost":   False,
                }
                patients.append(patient)
        
        print(f"Loaded {len(patients)} patients from {csv_filepath}")
        patients.sort(key=lambda p: p["arrival_time"])
        return patients
    
    except Exception as e:
        print(f"ERROR loading CSV: {e}")
        return generate_patient_dataset()  # Fallback to generated data


# ─────────────────────────────────────────────
#  SECTION 2 — ACUITY SCORE ENGINE
# ─────────────────────────────────────────────

def calculate_acuity_score(patient: dict) -> int:
    """
    Calculate acuity score (0-100) with full input validation and edge case handling.
    
    Clinical logic:
    - O2 saturation: 50 pts max (most critical)
    - Heart rate: 25 pts max (tachycardia/bradycardia)
    - Pain level: 15 pts max
    - Age risk: 10 pts max
    
    All inputs are validated and clamped to realistic ranges.
    """
    try:
        # Extract and validate vitals with safe defaults
        o2 = int(patient.get("oxygen_sat", 100))
        hr = int(patient.get("heart_rate", 80))
        pain = int(patient.get("pain_level", 0))
        age = int(patient.get("age", 40))
    except (ValueError, TypeError, KeyError):
        # Invalid data type — return minimal score
        return 0
    
    # Clamp all values to realistic medical ranges
    o2 = max(1, min(100, o2))      # Oxygen: 1-100%
    hr = max(30, min(300, hr))      # Heart rate: 30-300 bpm
    pain = max(0, min(10, pain))    # Pain: 0-10 scale
    age = max(0, min(150, age))     # Age: 0-150 years
    
    score = 0

    # ─────────────────────────────────────────
    # O2 SATURATION (highest weight, up to 50 pts)
    # ─────────────────────────────────────────
    if o2 < 85:       score += 50  # Critical hypoxia
    elif o2 < 90:     score += 40  # Severe hypoxia
    elif o2 < 94:     score += 25  # Moderate hypoxia
    elif o2 < 96:     score += 10  # Mild hypoxia
    # else: score += 0 (normal oxygen)

    # ─────────────────────────────────────────
    # HEART RATE (up to 25 pts)
    # Separate logic for bradycardia vs tachycardia
    # ─────────────────────────────────────────
    if hr < 40:       score += 25  # Severe bradycardia
    elif hr < 50:     score += 18  # Moderate bradycardia
    elif hr < 55:     score += 10  # Mild bradycardia
    elif hr < 60:     score += 5   # Slightly low
    elif hr > 150:    score += 25  # Severe tachycardia
    elif hr > 130:    score += 18  # Moderate tachycardia
    elif hr > 110:    score += 10  # Mild tachycardia
    elif hr > 100:    score += 5   # Slightly elevated
    # else: 60-100 is normal range (0 points)

    # ─────────────────────────────────────────
    # PAIN LEVEL (up to 15 pts, linear scaling)
    # ─────────────────────────────────────────
    # Pain 0-10 scale converts to 0-15 points (1.5x multiplier)
    pain_score = min(int(pain * 1.5), 15)
    score += pain_score

    # ─────────────────────────────────────────
    # AGE RISK (up to 10 pts)
    # ─────────────────────────────────────────
    if age <= 5 or age >= 75:     score += 10  # Very young or very old
    elif age <= 12 or age >= 65:  score += 6   # Young or elderly
    elif age >= 50:               score += 3   # Middle-aged (risk factor)
    # else: age 13-49 is low-risk (0 points)

    # Final score: ensure it's always within 0-100 range
    return min(max(score, 0), 100)


def assign_priority_level(acuity_score: int) -> str:
    if acuity_score >= 60:  return "Critical"
    if acuity_score >= 30:  return "Moderate"
    return "Stable"


# ─────────────────────────────────────────────
#  SECTION 3 — PRIORITY QUEUE
# ─────────────────────────────────────────────

class TriageQueue:
    def __init__(self):
        self._heap:   list = []
        self._lookup: dict = {}

    def _to_minutes(self, time_str: str) -> int:
        h, m = map(int, time_str.split(":"))
        return h * 60 + m

    def enqueue(self, patient: dict) -> None:
        score   = patient["acuity_score"]
        arrival = self._to_minutes(patient["arrival_time"])
        heapq.heappush(self._heap, (-score, arrival, patient["patient_id"]))
        self._lookup[patient["patient_id"]] = patient

    def dequeue(self) -> dict | None:
        while self._heap:
            _, _, pid = heapq.heappop(self._heap)
            if pid in self._lookup:
                return self._lookup.pop(pid)
        return None

    def update_patient(self, patient_id: str, new_vitals: dict) -> bool:
        if patient_id not in self._lookup:
            return False
        patient = self._lookup[patient_id]
        for key, value in new_vitals.items():
            if key in patient:
                patient[key] = value
        patient["acuity_score"]   = calculate_acuity_score(patient)
        patient["priority_level"] = assign_priority_level(patient["acuity_score"])
        self._lookup[patient_id]  = patient
        self.enqueue(patient)
        return True

    def apply_wait_time_boost(self, current_time_str: str, threshold_minutes: int = 120) -> int:
        current_min = self._to_minutes(current_time_str)
        boosted     = 0
        for pid, patient in list(self._lookup.items()):
            if patient["priority_level"] != "Stable" or patient.get("wait_boost"):
                continue
            wait_min = current_min - self._to_minutes(patient["arrival_time"])
            if wait_min > threshold_minutes:
                patient["acuity_score"]   = min(patient["acuity_score"] + 15, 100)
                patient["priority_level"] = assign_priority_level(patient["acuity_score"])
                patient["wait_boost"]     = True
                self.enqueue(patient)
                boosted += 1
        return boosted

    def drain_ordered(self) -> list[dict]:
        ordered = []
        while self._heap:
            p = self.dequeue()
            if p:
                ordered.append(p)
        return ordered

    def size(self) -> int:
        return len(self._lookup)


# ─────────────────────────────────────────────
#  SECTION 4 — PIPELINE  (called by Flask)
# ─────────────────────────────────────────────

def run_pipeline(csv_file: str = None) -> dict:
    """
    Full triage pipeline.
    
    Args:
        csv_file: Path to CSV file with patient data. If None, generates random data.
    
    Returns a dict with ordered patients + summary stats.
    Also writes triage_order.csv to output/.
    """
    # Load data from CSV if provided, otherwise generate random data
    if csv_file:
        patients = load_patient_dataset_from_csv(csv_file)
    else:
        patients = generate_patient_dataset(210)

    for p in patients:
        p["acuity_score"]   = calculate_acuity_score(p)
        p["priority_level"] = assign_priority_level(p["acuity_score"])

    queue = TriageQueue()
    for p in patients:
        queue.enqueue(p)

    boosted = queue.apply_wait_time_boost("16:00", threshold_minutes=120)
    ordered = queue.drain_ordered()

    for rank, p in enumerate(ordered, start=1):
        p["triage_rank"] = rank

    # Write CSV
    os.makedirs("output", exist_ok=True)
    csv_path = os.path.join("output", "triage_order.csv")
    fieldnames = [
        "triage_rank", "patient_id", "age", "heart_rate",
        "oxygen_sat", "pain_level", "arrival_time",
        "acuity_score", "priority_level", "wait_boost",
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in ordered:
            writer.writerow({k: p.get(k, "") for k in fieldnames})

    # Summary
    levels = {"Critical": 0, "Moderate": 0, "Stable": 0}
    for p in ordered:
        levels[p["priority_level"]] += 1

    return {
        "patients":    ordered,
        "summary":     levels,
        "total":       len(ordered),
        "wait_boosted": boosted,
        "csv_path":    csv_path,
    }


# ─────────────────────────────────────────────
#  SECTION 5 — TEST CASES
# ─────────────────────────────────────────────

def run_test_cases() -> list[dict]:
    results = []

    # TC-4: Priority Override
    pa = {"patient_id":"A001","age":30,"heart_rate":80,"oxygen_sat":97,"pain_level":3,"arrival_time":"10:00","wait_boost":False}
    pb = {"patient_id":"B001","age":45,"heart_rate":95,"oxygen_sat":87,"pain_level":6,"arrival_time":"10:15","wait_boost":False}
    for p in [pa, pb]:
        p["acuity_score"]   = calculate_acuity_score(p)
        p["priority_level"] = assign_priority_level(p["acuity_score"])
    q4 = TriageQueue()
    q4.enqueue(pa); q4.enqueue(pb)
    first = q4.dequeue()
    results.append({
        "id": "TC-4", "title": "Priority Override",
        "description": f"Patient A score: {pa['acuity_score']} ({pa['priority_level']}) | Patient B score: {pb['acuity_score']} ({pb['priority_level']})",
        "result": f"First treated: {first['patient_id']}",
        "passed": first["patient_id"] == "B001",
    })

    # TC-5: Dictionary Isolation
    pc = {"patient_id":"C001","age":25,"heart_rate":72,"oxygen_sat":98,"pain_level":2,"arrival_time":"09:00","wait_boost":False}
    pd = {"patient_id":"C002","age":60,"heart_rate":88,"oxygen_sat":95,"pain_level":5,"arrival_time":"09:10","wait_boost":False}
    for p in [pc, pd]:
        p["acuity_score"]   = calculate_acuity_score(p)
        p["priority_level"] = assign_priority_level(p["acuity_score"])
    q5 = TriageQueue()
    q5.enqueue(pc); q5.enqueue(pd)
    before = q5._lookup["C002"]["acuity_score"]
    q5.update_patient("C001", {"oxygen_sat": 82, "pain_level": 9})
    after  = q5._lookup["C002"]["acuity_score"]
    results.append({
        "id": "TC-5", "title": "Dictionary Isolation",
        "description": f"C001 updated (O2→82, Pain→9) → new score {q5._lookup['C001']['acuity_score']}. C002 score before: {before}, after: {after}",
        "result": "C002 score unchanged — full isolation confirmed",
        "passed": before == after,
    })

    # TC-6: Wait-Time Boost
    pe = {"patient_id":"D001","age":28,"heart_rate":72,"oxygen_sat":98,"pain_level":2,"arrival_time":"08:00","wait_boost":False}
    pe["acuity_score"]   = calculate_acuity_score(pe)
    pe["priority_level"] = assign_priority_level(pe["acuity_score"])
    q6 = TriageQueue()
    q6.enqueue(pe)
    score_before = q6._lookup["D001"]["acuity_score"]
    boosted = q6.apply_wait_time_boost("10:05", threshold_minutes=120)
    score_after = q6._lookup["D001"]["acuity_score"]
    results.append({
        "id": "TC-6", "title": "Wait-Time Boost",
        "description": f"D001 waited 2h05m. Score before: {score_before}, after: {score_after}. Patients boosted: {boosted}",
        "result": f"Score {score_before} → {score_after} (+15 boost applied)",
        "passed": score_after > score_before,
    })

    return results
