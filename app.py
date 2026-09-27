from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sqlite3

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "hospital-krr-development-secret-key-2026"
)

DATABASE = "hospital.db"


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =====================================================
# CREATE TABLES AND SAMPLE DATA
# =====================================================

def init_db():

    conn = get_db_connection()
    cursor = conn.cursor()

    # =================================================
    # PATIENTS TABLE
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            disease TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    # =================================================
    # DOCTORS TABLE
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)

    # =================================================
    # BEDS TABLE
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS beds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bed_number TEXT NOT NULL UNIQUE,
            ward TEXT NOT NULL,
            bed_type TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    # =================================================
    # KRR ASSESSMENT HISTORY TABLE
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS krr_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symptoms TEXT NOT NULL,
            matched_rule TEXT NOT NULL,
            recommendation TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # =================================================
    # SAMPLE PATIENTS
    # =================================================

    patient_count = cursor.execute(
        "SELECT COUNT(*) FROM patients"
    ).fetchone()[0]

    if patient_count == 0:

        sample_patients = [
            (
                "Rahul Sharma",
                25,
                "Male",
                "Fever",
                "9876543210"
            ),
            (
                "Priya Patel",
                30,
                "Female",
                "Diabetes",
                "9876501234"
            ),
            (
                "Amit Verma",
                45,
                "Male",
                "Blood Pressure",
                "9988776655"
            ),
            (
                "Sneha Joshi",
                22,
                "Female",
                "Malaria",
                "9123456780"
            ),
            (
                "Rohan Desai",
                55,
                "Male",
                "Heart Problem",
                "9012345678"
            )
        ]

        cursor.executemany("""
            INSERT INTO patients
            (name, age, gender, disease, phone)
            VALUES (?, ?, ?, ?, ?)
        """, sample_patients)

    # =================================================
    # SAMPLE DOCTORS
    # =================================================

    doctor_count = cursor.execute(
        "SELECT COUNT(*) FROM doctors"
    ).fetchone()[0]

    if doctor_count == 0:

        sample_doctors = [
            (
                "Dr. Rajesh Mehta",
                "Cardiologist",
                "9876541111",
                "rajesh@hospital.com"
            ),
            (
                "Dr. Anjali Deshmukh",
                "General Physician",
                "9876542222",
                "anjali@hospital.com"
            ),
            (
                "Dr. Vikram Singh",
                "Neurologist",
                "9876543333",
                "vikram@hospital.com"
            ),
            (
                "Dr. Neha Kulkarni",
                "Dermatologist",
                "9876544444",
                "neha@hospital.com"
            ),
            (
                "Dr. Arjun Patil",
                "Orthopedic",
                "9876545555",
                "arjun@hospital.com"
            )
        ]

        cursor.executemany("""
            INSERT INTO doctors
            (doctor_name, specialization, phone, email)
            VALUES (?, ?, ?, ?)
        """, sample_doctors)

    # =================================================
    # SAMPLE BEDS
    # =================================================

    bed_count = cursor.execute(
        "SELECT COUNT(*) FROM beds"
    ).fetchone()[0]

    if bed_count == 0:

        sample_beds = [
            (
                "B-101",
                "General Ward",
                "Single Bed",
                "Available"
            ),
            (
                "B-102",
                "General Ward",
                "Single Bed",
                "Occupied"
            ),
            (
                "B-103",
                "ICU",
                "ICU Bed",
                "Available"
            ),
            (
                "B-104",
                "ICU",
                "ICU Bed",
                "Occupied"
            ),
            (
                "B-105",
                "Emergency Ward",
                "Emergency Bed",
                "Available"
            ),
            (
                "B-106",
                "Private Ward",
                "Single Bed",
                "Available"
            ),
            (
                "B-107",
                "General Ward",
                "Double Bed",
                "Available"
            ),
            (
                "B-108",
                "Private Ward",
                "Single Bed",
                "Occupied"
            )
        ]

        cursor.executemany("""
            INSERT INTO beds
            (bed_number, ward, bed_type, status)
            VALUES (?, ?, ?, ?)
        """, sample_beds)

    conn.commit()
    conn.close()

    print("SQLite database connected successfully!")
    print("Patients table is ready!")
    print("Doctors table is ready!")
    print("Beds table is ready!")
    print("Sample data inserted successfully!")


# =====================================================
# MEDICAL KNOWLEDGE REPRESENTATION AND REASONING
# =====================================================

MEDICAL_RULES = [
    {
        "symptoms": {"chest pain"},
        "matched_rule": "Urgent chest pain rule",
        "reason": (
            "Chest pain was selected, which satisfies this highest-priority rule."
        ),
        "rule": "IF chest pain THEN seek urgent medical evaluation.",
        "recommendation": (
            "Possible urgent cardiac or emergency concern. "
            "Please seek immediate evaluation from Emergency and Cardiology."
        )
    },
    {
        "symptoms": {"fever", "cough"},
        "matched_rule": "Respiratory infection rule",
        "reason": "Fever and cough were both selected.",
        "rule": "IF fever AND cough THEN possible respiratory infection.",
        "recommendation": (
            "Possible respiratory infection. "
            "Consider General Medicine or a Respiratory clinic."
        )
    },
    {
        "symptoms": {"headache", "vomiting"},
        "matched_rule": "Migraine-related condition rule",
        "reason": "Headache and vomiting were both selected.",
        "rule": "IF headache AND vomiting THEN possible migraine-related condition.",
        "recommendation": (
            "Possible migraine-related condition. "
            "Consider General Medicine or Neurology."
        )
    },
    {
        "symptoms": {"fever", "headache"},
        "matched_rule": "Viral illness rule",
        "reason": "Fever and headache were both selected.",
        "rule": "IF fever AND headache THEN possible viral illness.",
        "recommendation": (
            "Possible viral illness. Consider General Medicine."
        )
    },
    {
        "symptoms": {"cough", "sore throat"},
        "matched_rule": "Throat or respiratory condition rule",
        "reason": "Cough and sore throat were both selected.",
        "rule": (
            "IF cough AND sore throat "
            "THEN possible throat or respiratory condition."
        ),
        "recommendation": (
            "Possible throat or respiratory condition. "
            "Consider General Medicine or a Respiratory clinic."
        )
    },
    {
        "symptoms": {"vomiting", "abdominal pain"},
        "matched_rule": "Digestive condition rule",
        "reason": "Vomiting and abdominal pain were both selected.",
        "rule": (
            "IF vomiting AND abdominal pain "
            "THEN possible digestive condition."
        ),
        "recommendation": (
            "Possible digestive condition. Consider General Medicine."
        )
    },
    {
        "symptoms": {"fever"},
        "matched_rule": "Fever rule",
        "reason": "Fever was selected.",
        "rule": "IF fever THEN possible infection.",
        "recommendation": "Possible infection. Consider General Medicine."
    },
    {
        "symptoms": {"cough"},
        "matched_rule": "Cough rule",
        "reason": "Cough was selected.",
        "rule": "IF cough THEN possible respiratory concern.",
        "recommendation": (
            "Possible respiratory concern. "
            "Consider General Medicine or a Respiratory clinic."
        )
    }
]


def find_medical_rule(selected_symptoms):
    """Return the first rule whose symptoms are all selected."""

    selected_symptom_set = set(selected_symptoms)

    for rule in MEDICAL_RULES:
        if rule["symptoms"].issubset(selected_symptom_set):
            return rule

    return {
        "matched_rule": "No matching rule",
        "reason": (
            "The selected symptoms do not satisfy all IF conditions of any "
            "predefined rule."
        ),
        "rule": "No predefined rule matched the selected symptoms.",
        "recommendation": (
            "No educational recommendation is available for this symptom "
            "combination. Please consult a qualified healthcare professional."
        )
    }


def evaluate_medical_rules(selected_symptoms):
    """Evaluate every rule while preserving the existing priority order."""

    selected_symptom_set = set(selected_symptoms)
    selected_rule_found = False
    evaluation_trace = []

    for priority, rule in enumerate(MEDICAL_RULES, start=1):
        is_matched = rule["symptoms"].issubset(selected_symptom_set)

        if is_matched and not selected_rule_found:
            status = "Matched and selected"
            status_class = "selected"
            selected_rule_found = True
        elif is_matched:
            status = "Matched but lower priority"
            status_class = "lower-priority"
        else:
            status = "Not matched"
            status_class = "not-matched"

        evaluation_trace.append({
            "priority": priority,
            "matched_rule": rule["matched_rule"],
            "rule": rule["rule"],
            "status": status,
            "status_class": status_class
        })

    return evaluation_trace


# =====================================================
# DASHBOARD
# =====================================================

@app.route("/")
def index():

    conn = get_db_connection()

    # Counts
    patient_count = conn.execute("""
        SELECT COUNT(*) AS total
        FROM patients
    """).fetchone()["total"]

    doctor_count = conn.execute("""
        SELECT COUNT(*) AS total
        FROM doctors
    """).fetchone()["total"]

    bed_count = conn.execute("""
        SELECT COUNT(*) AS total
        FROM beds
    """).fetchone()["total"]

    available_beds = conn.execute("""
        SELECT COUNT(*) AS total
        FROM beds
        WHERE status = 'Available'
    """).fetchone()["total"]

    occupied_beds = conn.execute("""
        SELECT COUNT(*) AS total
        FROM beds
        WHERE status = 'Occupied'
    """).fetchone()["total"]

    # Recent records
    recent_patients = conn.execute("""
        SELECT *
        FROM patients
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()

    recent_doctors = conn.execute("""
        SELECT *
        FROM doctors
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()

    recent_beds = conn.execute("""
        SELECT *
        FROM beds
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        patient_count=patient_count,
        doctor_count=doctor_count,
        bed_count=bed_count,
        available_beds=available_beds,
        occupied_beds=occupied_beds,
        recent_patients=recent_patients,
        recent_doctors=recent_doctors,
        recent_beds=recent_beds
    )


# =====================================================
# MEDICAL KRR
# =====================================================

@app.route("/rules", methods=["GET", "POST"])
def rules():

    if request.method == "POST":
        selected_symptoms = request.form.getlist("symptoms")

        if not selected_symptoms:
            flash("Please select at least one symptom.", "danger")
            return redirect(url_for("rules"))

        matched_rule_data = find_medical_rule(selected_symptoms)
        evaluation_trace = evaluate_medical_rules(selected_symptoms)

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO krr_assessments
            (symptoms, matched_rule, recommendation)
            VALUES (?, ?, ?)
        """, (
            ", ".join(selected_symptoms),
            matched_rule_data["matched_rule"],
            matched_rule_data["recommendation"]
        ))
        conn.commit()
        conn.close()

        return render_template(
            "patient_result.html",
            symptoms=selected_symptoms,
            matched_rule=matched_rule_data["matched_rule"],
            match_reason=matched_rule_data["reason"],
            if_then_explanation=matched_rule_data["rule"],
            recommendation=matched_rule_data["recommendation"],
            evaluation_trace=evaluation_trace
        )

    return render_template("rules.html", medical_rules=MEDICAL_RULES)


@app.route("/krr-history")
def krr_history():
    query = request.args.get("q", "").strip()

    conn = get_db_connection()

    if query:
        like_query = f"%{query}%"

        assessments = conn.execute("""
            SELECT id, symptoms, matched_rule, recommendation, created_at
            FROM krr_assessments
            WHERE symptoms LIKE ?
               OR matched_rule LIKE ?
               OR recommendation LIKE ?
            ORDER BY created_at DESC, id DESC
        """, (
            like_query,
            like_query,
            like_query
        )).fetchall()

    else:
        assessments = conn.execute("""
            SELECT id, symptoms, matched_rule, recommendation, created_at
            FROM krr_assessments
            ORDER BY created_at DESC, id DESC
        """).fetchall()

    conn.close()

    return render_template(
        "krr_history.html",
        assessments=assessments,
        query=query
    )


# =====================================================
# PATIENTS
# =====================================================

@app.route("/patients", methods=["GET", "POST"])
def patients():

    conn = get_db_connection()

    if request.method == "POST":

        name = request.form.get("name")
        age = request.form.get("age")
        gender = request.form.get("gender")
        disease = request.form.get("disease")
        phone = request.form.get("phone")

        if not name or not age or not gender or not disease or not phone:

            flash("Please fill all patient details.", "danger")
            conn.close()

            return redirect(url_for("patients"))

        conn.execute("""
            INSERT INTO patients
            (name, age, gender, disease, phone)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            age,
            gender,
            disease,
            phone
        ))

        conn.commit()
        conn.close()

        flash("Patient added successfully!", "success")

        return redirect(url_for("patients"))

    patients_data = conn.execute("""
        SELECT *
        FROM patients
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "patients.html",
        patients=patients_data
    )


@app.route("/delete-patient/<int:patient_id>", methods=["POST"])
def delete_patient(patient_id):

    conn = get_db_connection()

    conn.execute("""
        DELETE FROM patients
        WHERE id = ?
    """, (patient_id,))

    conn.commit()
    conn.close()

    flash("Patient deleted successfully!", "success")

    return redirect(url_for("patients"))


# =====================================================
# DOCTORS
# =====================================================

@app.route("/doctors", methods=["GET", "POST"])
def doctors():

    conn = get_db_connection()

    if request.method == "POST":

        doctor_name = request.form.get("doctor_name")
        specialization = request.form.get("specialization")
        phone = request.form.get("phone")
        email = request.form.get("email")

        if not doctor_name or not specialization or not phone or not email:

            flash("Please fill all doctor details.", "danger")
            conn.close()

            return redirect(url_for("doctors"))

        conn.execute("""
            INSERT INTO doctors
            (doctor_name, specialization, phone, email)
            VALUES (?, ?, ?, ?)
        """, (
            doctor_name,
            specialization,
            phone,
            email
        ))

        conn.commit()
        conn.close()

        flash("Doctor added successfully!", "success")

        return redirect(url_for("doctors"))

    doctors_data = conn.execute("""
        SELECT *
        FROM doctors
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "doctors.html",
        doctors=doctors_data
    )


@app.route("/delete-doctor/<int:doctor_id>", methods=["POST"])
def delete_doctor(doctor_id):

    conn = get_db_connection()

    conn.execute("""
        DELETE FROM doctors
        WHERE id = ?
    """, (doctor_id,))

    conn.commit()
    conn.close()

    flash("Doctor deleted successfully!", "success")

    return redirect(url_for("doctors"))


# =====================================================
# BEDS
# =====================================================

@app.route("/beds", methods=["GET", "POST"])
def beds():

    conn = get_db_connection()

    if request.method == "POST":

        bed_number = request.form.get("bed_number")
        ward = request.form.get("ward")
        bed_type = request.form.get("bed_type")
        status = request.form.get("status")

        if not bed_number or not ward or not bed_type or not status:

            flash("Please fill all bed details.", "danger")
            conn.close()

            return redirect(url_for("beds"))

        try:

            conn.execute("""
                INSERT INTO beds
                (bed_number, ward, bed_type, status)
                VALUES (?, ?, ?, ?)
            """, (
                bed_number,
                ward,
                bed_type,
                status
            ))

            conn.commit()
            conn.close()

            flash("Bed added successfully!", "success")

            return redirect(url_for("beds"))

        except sqlite3.IntegrityError:

            conn.close()

            flash(
                "This bed number already exists.",
                "danger"
            )

            return redirect(url_for("beds"))

    beds_data = conn.execute("""
        SELECT *
        FROM beds
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "beds.html",
        beds=beds_data
    )


@app.route("/delete-bed/<int:bed_id>", methods=["POST"])
def delete_bed(bed_id):

    conn = get_db_connection()

    conn.execute("""
        DELETE FROM beds
        WHERE id = ?
    """, (bed_id,))

    conn.commit()
    conn.close()

    flash("Bed deleted successfully!", "success")

    return redirect(url_for("beds"))


# =====================================================
# START SERVER
# =====================================================

if __name__ == "__main__":

    init_db()

    print("Hospital KRR System is running!")
    print("Open: http://127.0.0.1:5000")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
