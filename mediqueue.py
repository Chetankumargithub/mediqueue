"""
MediQueue – Emergency Triage Priority System
SDG 3: Good Health and Well-being
"""

import csv
import heapq
import random
import time
from datetime import datetime, timedelta


# ─────────────────────────────────────────────
#  SECTION 1 – DATASET GENERATION (200+ records)
# ─────────────────────────────────────────────

def generate_patient_dataset(num_patients: int = 210) -> list[dict]:
    """
    Synthesise a realistic ER patient dataset.
    Returns a list of patient dictionaries.
    """
    random.seed(42)  # Reproducible results

    # Vital-range presets to ensure a realistic mix
    presets = [
        # (weight, age_range, hr_range, o2_range, pain_range, label)
        (0.25, (18, 80), (100, 160), (80, 89),  (7, 10), "critical"),
        (0.35, (18, 80), (80,  130), (90, 94),  (5,  8), "moderate"),
        (0.40, (18, 80), (60,   90), (95, 100), (1,  4), "stable"),
    ]

    base_time = datetime(2024, 1, 15, 8, 0)   # ER opens at 08:00
    patients   = []

    for i in range(num_patients):
        pid = f"P{101 + i}"

        # Pick a preset proportionally
        r = random.random()
        if r < 0.25:
            preset = presets[0]
        elif r < 0.60:
            preset = presets[1]
        else:
            preset = presets[2]

        _, age_r, hr_r, o2_r, pain_r, _ = preset

        age        = random.randint(*age_r)
        heart_rate = random.randint(*hr_r)
        oxygen_sat = random.randint(*o2_r)
        pain_level = random.randint(*pain_r)

        # Arrival time: random spread over 8-hour shift
        offset_min  = random.randint(0, 480)
        arrival_dt  = base_time + timedelta(minutes=offset_min)
        arrival_str = arrival_dt.strftime("%H:%M")

        patients.append({
            "patient_id":   pid,
            "age":          age,
            "heart_rate":   heart_rate,
            "oxygen_sat":   oxygen_sat,
            "pain_level":   pain_level,
            "arrival_time": arrival_str,
        })

    # Sort by arrival so the queue feels realistic
    patients.sort(key=lambda p: p["arrival_time"])
    return patients


# ─────────────────────────────────────────────
#  SECTION 2 – ACUITY SCORE ENGINE
# ─────────────────────────────────────────────

def calculate_acuity_score(patient: dict) -> int:
    """
    Compute an integer Acuity Score (0–100) from patient vitals.

    Scoring formula (higher = more critical):
      Oxygen saturation penalty  : up to 50 pts
      Heart-rate deviation       : up to 25 pts
      Pain level                 : up to 15 pts
      Age risk factor            : up to 10 pts
    """
    score = 0

    # 1. Oxygen saturation (most critical vital)
    o2 = patient["oxygen_sat"]
    if o2 < 85:
        score += 50
    elif o2 < 90:
        score += 40
    elif o2 < 94:
        score += 25
    elif o2 < 96:
        score += 10
    else:
        score += 0

    # 2. Heart rate deviation from normal (60–100 bpm)
    hr = patient["heart_rate"]
    if hr > 150 or hr < 40:
        score += 25
    elif hr > 130 or hr < 50:
        score += 18
    elif hr > 110 or hr < 55:
        score += 10
    elif hr > 100 or hr < 60:
        score += 5
    else:
        score += 0

    # 3. Pain level (1–10 scale)
    pain = patient["pain_level"]
    if pain >= 9:
        score += 15
    elif pain >= 7:
        score += 10
    elif pain >= 5:
        score += 5
    elif pain >= 3:
        score += 2
    else:
        score += 0

    # 4. Age-related risk
    age = patient["age"]
    if age >= 75 or age <= 5:
        score += 10
    elif age >= 65 or age <= 12:
        score += 6
    elif age >= 50:
        score += 3
    else:
        score += 0

    return min(score, 100)


def assign_priority_level(acuity_score: int) -> str:
    """Map numeric acuity score to a named triage level."""
    if acuity_score >= 60:
        return "Critical"
    elif acuity_score >= 30:
        return "Moderate"
    else:
        return "Stable"


# ─────────────────────────────────────────────
#  SECTION 3 – PRIORITY QUEUE  (min-heap trick)
# ─────────────────────────────────────────────

class TriageQueue:
    """
    Max-priority queue backed by a min-heap.
    Higher acuity scores are dequeued first.
    Tie-breaks on arrival time (earlier = higher priority).
    """

    def __init__(self):
        self._heap   : list = []
        self._lookup : dict = {}   # patient_id → patient dict

    def _to_minutes(self, time_str: str) -> int:
        h, m = map(int, time_str.split(":"))
        return h * 60 + m

    def enqueue(self, patient: dict) -> None:
        score    = patient["acuity_score"]
        arrival  = self._to_minutes(patient["arrival_time"])
        # Negate score so the smallest heap value = highest priority
        heap_key = (-score, arrival, patient["patient_id"])
        heapq.heappush(self._heap, heap_key)
        self._lookup[patient["patient_id"]] = patient

    def dequeue(self) -> dict | None:
        while self._heap:
            _, _, pid = heapq.heappop(self._heap)
            if pid in self._lookup:
                return self._lookup.pop(pid)
        return None

    def update_patient(self, patient_id: str, new_vitals: dict) -> bool:
        """
        TEST CASE 5 – Dictionary lookup / update.
        Update a patient's vitals in-place without affecting other records.
        The heap is lazily rebuilt on next dequeue.
        """
        if patient_id not in self._lookup:
            return False

        patient = self._lookup[patient_id]
        # Only update the supplied vitals keys
        for key, value in new_vitals.items():
            if key in patient:
                patient[key] = value

        # Recalculate acuity and re-enqueue (old entry left as tombstone)
        patient["acuity_score"]   = calculate_acuity_score(patient)
        patient["priority_level"] = assign_priority_level(patient["acuity_score"])
        self._lookup[patient_id]  = patient
        self.enqueue(patient)      # Old key becomes orphaned tombstone
        return True

    def apply_wait_time_boost(self, current_time_str: str, threshold_minutes: int = 120) -> int:
        """
        TEST CASE 6 – Wait-time boost.
        Low-priority patients waiting > threshold get +15 score to prevent starvation.
        Returns the number of patients boosted.
        """
        current_min = self._to_minutes(current_time_str)
        boosted     = 0

        for pid, patient in self._lookup.items():
            if patient["priority_level"] != "Stable":
                continue
            arrival_min = self._to_minutes(patient["arrival_time"])
            wait_min    = current_min - arrival_min
            if wait_min > threshold_minutes:
                patient["acuity_score"]   = min(patient["acuity_score"] + 15, 100)
                patient["priority_level"] = assign_priority_level(patient["acuity_score"])
                patient["wait_boost"]     = True
                self.enqueue(patient)
                boosted += 1

        return boosted

    def drain_ordered(self) -> list[dict]:
        """Dequeue all patients in priority order."""
        ordered = []
        while self._heap:
            p = self.dequeue()
            if p:
                ordered.append(p)
        return ordered

    def size(self) -> int:
        return len(self._lookup)


# ─────────────────────────────────────────────
#  SECTION 4 – TEST CASES
# ─────────────────────────────────────────────

def run_test_cases():
    print("\n" + "=" * 60)
    print("  MEDIQUEUE – TEST CASE VALIDATION")
    print("=" * 60)

    # ── Test Case 4: Priority Override (O2 < 90) ──────────────
    print("\n[TEST 4] Priority Override – Low O2 jumps ahead")
    patient_a = {
        "patient_id": "A001", "age": 30,
        "heart_rate": 80,  "oxygen_sat": 97,
        "pain_level": 3,   "arrival_time": "10:00",
    }
    patient_b = {
        "patient_id": "B001", "age": 45,
        "heart_rate": 95,  "oxygen_sat": 87,   # <90 → critical
        "pain_level": 6,   "arrival_time": "10:15",
    }
    for p in [patient_a, patient_b]:
        p["acuity_score"]   = calculate_acuity_score(p)
        p["priority_level"] = assign_priority_level(p["acuity_score"])

    q4 = TriageQueue()
    q4.enqueue(patient_a)
    q4.enqueue(patient_b)
    first = q4.dequeue()
    print(f"  Patient A score: {patient_a['acuity_score']} ({patient_a['priority_level']})")
    print(f"  Patient B score: {patient_b['acuity_score']} ({patient_b['priority_level']})")
    print(f"  ➜ First treated: {first['patient_id']}  ✓" if first["patient_id"] == "B001" else "  ✗ FAIL")

    # ── Test Case 5: Dictionary Lookup – isolation ─────────────
    print("\n[TEST 5] Dictionary Update – isolation check")
    patients_tc5 = [
        {"patient_id": "C001", "age": 25, "heart_rate": 72, "oxygen_sat": 98, "pain_level": 2, "arrival_time": "09:00"},
        {"patient_id": "C002", "age": 60, "heart_rate": 88, "oxygen_sat": 95, "pain_level": 5, "arrival_time": "09:10"},
    ]
    for p in patients_tc5:
        p["acuity_score"]   = calculate_acuity_score(p)
        p["priority_level"] = assign_priority_level(p["acuity_score"])

    q5 = TriageQueue()
    for p in patients_tc5:
        q5.enqueue(p)

    score_c002_before = q5._lookup["C002"]["acuity_score"]
    q5.update_patient("C001", {"oxygen_sat": 82, "pain_level": 9})
    score_c002_after  = q5._lookup["C002"]["acuity_score"]

    print(f"  C002 score before update of C001: {score_c002_before}")
    print(f"  C002 score after  update of C001: {score_c002_after}")
    print(f"  C001 new acuity: {q5._lookup['C001']['acuity_score']} ({q5._lookup['C001']['priority_level']})")
    print(f"  ➜ Isolation:   {'✓ PASS' if score_c002_before == score_c002_after else '✗ FAIL'}")

    # ── Test Case 6: Wait-time boost ──────────────────────────
    print("\n[TEST 6] Wait-Time Boost – >2 hrs stable patient")
    stable_patient = {
        "patient_id": "D001", "age": 28, "heart_rate": 72,
        "oxygen_sat": 98, "pain_level": 2, "arrival_time": "08:00",
        "wait_boost": False,
    }
    stable_patient["acuity_score"]   = calculate_acuity_score(stable_patient)
    stable_patient["priority_level"] = assign_priority_level(stable_patient["acuity_score"])

    q6 = TriageQueue()
    q6.enqueue(stable_patient)
    score_before = q6._lookup["D001"]["acuity_score"]
    boosted = q6.apply_wait_time_boost("10:05", threshold_minutes=120)  # 2h05 wait
    score_after = q6._lookup["D001"]["acuity_score"]

    print(f"  Score before boost: {score_before}")
    print(f"  Score after  boost: {score_after}")
    print(f"  Patients boosted:   {boosted}")
    print(f"  ➜ Boost applied:   {'✓ PASS' if score_after > score_before else '✗ FAIL'}")


# ─────────────────────────────────────────────
#  SECTION 5 – MAIN PIPELINE
# ─────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  MediQueue – Emergency Triage Priority System")
    print("  SDG 3: Good Health and Well-being")
    print("=" * 60)

    # 1. Generate dataset
    patients = generate_patient_dataset(210)
    print(f"\n[1/4] Generated {len(patients)} patient records.")

    # 2. Score every patient
    for p in patients:
        p["acuity_score"]   = calculate_acuity_score(p)
        p["priority_level"] = assign_priority_level(p["acuity_score"])
        p["wait_boost"]     = False

    # 3. Load into triage queue
    queue = TriageQueue()
    for p in patients:
        queue.enqueue(p)
    print(f"[2/4] Loaded {queue.size()} patients into triage queue.")

    # 4. Simulate wait-time boost at end of shift (16:00)
    boosted = queue.apply_wait_time_boost("16:00", threshold_minutes=120)
    print(f"[3/4] Wait-time boost applied to {boosted} long-waiting stable patients.")

    # 5. Drain queue in priority order
    ordered_patients = queue.drain_ordered()
    print(f"[4/4] Triage order resolved for {len(ordered_patients)} patients.\n")

    # 6. Write triage_order.csv
    csv_path = "/mnt/user-data/outputs/triage_order.csv"
    fieldnames = [
        "triage_rank", "patient_id", "age", "heart_rate",
        "oxygen_sat", "pain_level", "arrival_time",
        "acuity_score", "priority_level", "wait_boost",
    ]
    with open(csv_path, "w", newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        for rank, p in enumerate(ordered_patients, start=1):
            p["triage_rank"] = rank
            writer.writerow({k: p.get(k, "") for k in fieldnames})

    print(f"Output saved → {csv_path}")

    # 7. Summary statistics
    levels = {"Critical": 0, "Moderate": 0, "Stable": 0}
    for p in ordered_patients:
        levels[p["priority_level"]] += 1

    print("\n── Triage Summary ──────────────────────────")
    for lvl, cnt in levels.items():
        pct = cnt / len(ordered_patients) * 100
        print(f"  {lvl:<10}: {cnt:>3} patients  ({pct:.1f}%)")
    print("─────────────────────────────────────────────")
    print(f"  Total       : {len(ordered_patients)} patients")

    # 8. Show top-10 queue
    print("\n── Top 10 Priority Patients ─────────────────")
    print(f"  {'Rank':<5} {'ID':<6} {'Score':<7} {'Level':<10} {'HR':<5} {'O2':<5} {'Pain'}")
    for p in ordered_patients[:10]:
        print(
            f"  {p['triage_rank']:<5} {p['patient_id']:<6} "
            f"{p['acuity_score']:<7} {p['priority_level']:<10} "
            f"{p['heart_rate']:<5} {p['oxygen_sat']:<5} {p['pain_level']}"
        )

    # 9. Run validation test cases
    run_test_cases()

    return ordered_patients


if __name__ == "__main__":
    main()
