"""
app.py
Flask backend for MediQueue.
Run with: python app.py
Run with CSV file: set PATIENT_CSV=patient_data.csv && python app.py
Visit: http://localhost:5000
"""

from flask import Flask, jsonify, render_template, request, send_file
from flask_cors import CORS
from triage_engine import (
    run_pipeline,
    run_test_cases,
    calculate_acuity_score,
    assign_priority_level,
)
import os

app = Flask(__name__)
CORS(app)

# Primary dataset: Use realistic patient data from Downloads
CSV_FILE = r"C:\Users\Sumit and Chetan\Downloads\patient_data_realistic.csv"

# Verify the CSV file exists
if not os.path.exists(CSV_FILE):
    print(f"ERROR: Primary dataset file not found: {CSV_FILE}")
    print("Please ensure patient_data_realistic.csv is in your Downloads folder.")
    CSV_FILE = None
else:
    print(f"Dataset configured: {CSV_FILE}")

# In-memory state — reset each time pipeline runs
_state: dict = {}


def get_state() -> dict:
    global _state
    if not _state:
        if CSV_FILE:
            print(f"Loading patient data from: {CSV_FILE}")
            _state = run_pipeline(csv_file=CSV_FILE)
        else:
            print("ERROR: No dataset available. Please check CSV_FILE configuration.")
            _state = run_pipeline()  # Fallback (will never reach here normally)
    return _state


# ─────────────────────────────────────────────
#  PAGE ROUTE
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ─────────────────────────────────────────────
#  API ROUTES
# ─────────────────────────────────────────────

@app.route("/api/patients", methods=["GET"])
def api_patients():
    """Return all patients in triage order with summary stats."""
    state = get_state()
    return jsonify({
        "patients":     state["patients"],
        "summary":      state["summary"],
        "total":        state["total"],
        "wait_boosted": state["wait_boosted"],
    })


@app.route("/api/reset", methods=["POST"])
def api_reset():
    """Re-run the full pipeline (reload dataset)."""
    global _state
    if CSV_FILE:
        _state = run_pipeline(csv_file=CSV_FILE)
        message = "Dataset reloaded successfully."
    else:
        _state = run_pipeline()
        message = "Pipeline reset successfully."
    return jsonify({"message": message, "total": _state["total"]})


@app.route("/api/retriage", methods=["POST"])
def api_retriage():
    """
    Update a patient's vitals and recalculate their acuity score.
    Body: { patient_id, oxygen_sat?, heart_rate?, pain_level? }
    """
    state   = get_state()
    body    = request.get_json()
    pid     = body.get("patient_id")
    patient = next((p for p in state["patients"] if p["patient_id"] == pid), None)

    if not patient:
        return jsonify({"error": f"Patient {pid} not found"}), 404

    old_score = patient["acuity_score"]
    old_level = patient["priority_level"]

    for field in ["oxygen_sat", "heart_rate", "pain_level", "age"]:
        if field in body and body[field] is not None:
            patient[field] = int(body[field])

    patient["acuity_score"]   = calculate_acuity_score(patient)
    patient["priority_level"] = assign_priority_level(patient["acuity_score"])

    # Re-sort the queue
    state["patients"].sort(
        key=lambda p: (-p["acuity_score"], p["arrival_time"])
    )
    for rank, p in enumerate(state["patients"], start=1):
        p["triage_rank"] = rank

    # Update summary counts
    levels = {"Critical": 0, "Moderate": 0, "Stable": 0}
    for p in state["patients"]:
        levels[p["priority_level"]] += 1
    state["summary"] = levels

    return jsonify({
        "message":    f"{pid} re-triaged successfully",
        "patient_id": pid,
        "old_score":  old_score,
        "new_score":  patient["acuity_score"],
        "old_level":  old_level,
        "new_level":  patient["priority_level"],
        "new_rank":   patient["triage_rank"],
    })


@app.route("/api/waitboost", methods=["POST"])
def api_waitboost():
    """Apply +15 wait-time boost to stable patients waiting > 2 hours."""
    state   = get_state()
    body    = request.get_json() or {}
    cur_time = body.get("current_time", "16:00")

    def to_min(t):
        h, m = map(int, t.split(":"))
        return h * 60 + m

    boosted = 0
    cur_min = to_min(cur_time)

    for p in state["patients"]:
        if p["priority_level"] == "Stable" and not p.get("wait_boost"):
            wait = cur_min - to_min(p["arrival_time"])
            if wait > 120:
                p["acuity_score"]   = min(p["acuity_score"] + 15, 100)
                p["priority_level"] = assign_priority_level(p["acuity_score"])
                p["wait_boost"]     = True
                boosted += 1

    state["patients"].sort(key=lambda p: (-p["acuity_score"], p["arrival_time"]))
    for rank, p in enumerate(state["patients"], start=1):
        p["triage_rank"] = rank

    levels = {"Critical": 0, "Moderate": 0, "Stable": 0}
    for p in state["patients"]:
        levels[p["priority_level"]] += 1
    state["summary"] = levels
    state["wait_boosted"] = sum(1 for p in state["patients"] if p.get("wait_boost"))

    return jsonify({"message": f"Wait-boost applied to {boosted} patients", "boosted": boosted})


@app.route("/api/testcases", methods=["GET"])
def api_testcases():
    """Run and return validation test case results."""
    return jsonify(run_test_cases())


@app.route("/api/download-csv", methods=["GET"])
def api_download_csv():
    """Download the triage_order.csv file."""
    csv_path = os.path.join("output", "triage_order.csv")
    if not os.path.exists(csv_path):
        get_state()   # ensure CSV is generated
    return send_file(csv_path, as_attachment=True, download_name="triage_order.csv")


# ─────────────────────────────────────────────
#  RUN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  MediQueue — Starting server")
    print("  Visit: http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)
