"""
Synthetic data generator for Wasatch Family Health Clinic -- Project 3 (SQL Analytics).

Generates a realistic-but-synthetic clinical operations dataset (patients,
providers, appointments, encounters) into a SQLite database, seeded for
reproducibility. This is a self-generated synthetic dataset (no real patient
data), built to mirror the kind of encounter/appointment-level data a clinic's
practice-management or EHR system would produce, in the same spirit as
MITRE's Synthea patient generator.

Also loads the Project 2 ServiceNow ticket log (12 incidents) into a tickets
table, with reasonable resolution timestamps reconstructed for the
Resolved/Closed tickets so SLA compliance and resolution-time queries are
possible (the original ServiceNow demo tracked state, not full timestamps).
"""

import sqlite3
import random
from datetime import datetime, timedelta

random.seed(42)

DB_PATH = "wasatch_clinic_ops.db"

FIRST_NAMES = [
    "James","Mary","Robert","Patricia","John","Jennifer","Michael","Linda","David","Elizabeth",
    "William","Barbara","Richard","Susan","Joseph","Jessica","Thomas","Sarah","Charles","Karen",
    "Christopher","Nancy","Daniel","Lisa","Matthew","Betty","Anthony","Margaret","Mark","Sandra",
    "Donald","Ashley","Steven","Kimberly","Paul","Emily","Andrew","Donna","Joshua","Michelle",
    "Kenneth","Dorothy","Kevin","Carol","Brian","Amanda","George","Melissa","Timothy","Deborah",
    "Ronald","Stephanie","Edward","Rebecca","Jason","Sharon","Jeffrey","Laura","Ryan","Cynthia",
    "Jacob","Kathleen","Gary","Amy","Nicholas","Shirley","Eric","Angela","Jonathan","Helen",
    "Stephen","Anna","Larry","Brenda","Justin","Pamela","Scott","Nicole","Brandon","Emma",
    "Benjamin","Samantha","Samuel","Katherine","Gregory","Christine","Alexander","Debra","Patrick","Rachel",
    "Frank","Catherine","Raymond","Carolyn","Jack","Janet","Dennis","Ruth","Jerry","Maria",
]
LAST_NAMES = [
    "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
    "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
    "Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson",
    "Walker","Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores",
    "Green","Adams","Nelson","Baker","Hall","Rivera","Campbell","Mitchell","Carter","Roberts",
    "Gomez","Phillips","Evans","Turner","Diaz","Parker","Cruz","Edwards","Collins","Reyes",
    "Stewart","Morris","Morales","Murphy","Cook","Rogers","Gutierrez","Ortiz","Morgan","Cooper",
    "Peterson","Bailey","Reed","Kelly","Howard","Ramos","Kim","Cox","Ward","Richardson",
]

DEPARTMENTS = [
    ("Primary Care", "Family Medicine"),
    ("Pediatrics", "Pediatrics"),
    ("Behavioral Health", "Behavioral Health"),
    ("Physical Therapy", "Physical Therapy"),
    ("Urgent Care Walk-In", "Urgent Care"),
    ("Lab & Imaging", "Diagnostic Services"),
]

PROVIDER_NAMES_PER_DEPT = 3

APPOINTMENT_TYPES = ["New Patient", "Follow-Up", "Wellness/Annual", "Urgent", "Therapy Session", "Lab/Imaging Order"]

NO_SHOW_RATE = {
    "Primary Care": 0.09,
    "Pediatrics": 0.07,
    "Behavioral Health": 0.19,
    "Physical Therapy": 0.15,
    "Urgent Care Walk-In": 0.05,
    "Lab & Imaging": 0.04,
}

CANCEL_RATE = 0.06

DEPT_VOLUME_WEIGHT = {
    "Primary Care": 1.35,
    "Pediatrics": 1.05,
    "Urgent Care Walk-In": 1.2,
    "Lab & Imaging": 1.0,
    "Physical Therapy": 0.75,
    "Behavioral Health": 0.65,
}

WINDOW_DAYS = 182
TODAY = datetime(2026, 7, 29)
START = TODAY - timedelta(days=WINDOW_DAYS)

N_PATIENTS = 220
APPTS_PER_DAY_RANGE = (14, 26)


def business_days(start, end):
    d = start
    while d <= end:
        if d.weekday() < 5:
            yield d
        d += timedelta(days=1)


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(open("schema.sql").read())

    patients = []
    for i in range(1, N_PATIENTS + 1):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        age = random.choices(
            population=[random.randint(0, 12), random.randint(13, 17), random.randint(18, 39),
                        random.randint(40, 64), random.randint(65, 89)],
            weights=[0.14, 0.07, 0.28, 0.30, 0.21],
        )[0]
        dob = (TODAY - timedelta(days=age * 365 + random.randint(0, 364))).strftime("%Y-%m-%d")
        gender = random.choice(["F", "M"])
        patients.append((i, fn, ln, dob, gender))
    cur.executemany("INSERT INTO patients VALUES (?,?,?,?,?)", patients)

    dept_ids = {}
    for idx, (name, specialty) in enumerate(DEPARTMENTS, start=1):
        cur.execute("INSERT INTO departments VALUES (?,?,?)", (idx, name, specialty))
        dept_ids[name] = idx

    providers = []
    pid = 1
    dept_providers = {name: [] for name, _ in DEPARTMENTS}
    for name, specialty in DEPARTMENTS:
        for _ in range(PROVIDER_NAMES_PER_DEPT):
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            providers.append((pid, f"{fn} {ln}", specialty, dept_ids[name]))
            dept_providers[name].append(pid)
            pid += 1
    cur.executemany("INSERT INTO providers VALUES (?,?,?,?)", providers)

    appt_id = 1
    enc_id = 1
    appointments = []
    encounters = []

    patient_dept_history = {}

    for day in business_days(START, TODAY):
        n_today = random.randint(*APPTS_PER_DAY_RANGE)
        for _ in range(n_today):
            dept_name, specialty = random.choices(
                population=DEPARTMENTS,
                weights=[DEPT_VOLUME_WEIGHT[name] for name, _ in DEPARTMENTS],
            )[0]
            dept_id = dept_ids[dept_name]
            provider_id = random.choice(dept_providers[dept_name])
            patient_id = random.randint(1, N_PATIENTS)
            appt_type = (
                "Urgent" if dept_name == "Urgent Care Walk-In"
                else "Therapy Session" if dept_name == "Physical Therapy"
                else "Lab/Imaging Order" if dept_name == "Lab & Imaging"
                else random.choice(["New Patient", "Follow-Up", "Wellness/Annual"])
            )
            scheduled_dt = day + timedelta(hours=random.randint(8, 16), minutes=random.choice([0, 15, 30, 45]))

            roll = random.random()
            no_show_rate = NO_SHOW_RATE[dept_name]
            if roll < no_show_rate:
                status = "No-Show"
            elif roll < no_show_rate + CANCEL_RATE:
                status = "Cancelled"
            else:
                status = "Completed"

            encounter_id = None
            if status == "Completed":
                encounter_class = (
                    "emergency" if dept_name == "Urgent Care Walk-In" and random.random() < 0.12
                    else "urgent" if dept_name == "Urgent Care Walk-In"
                    else "wellness" if appt_type == "Wellness/Annual"
                    else "ambulatory"
                )
                reason = {
                    "Primary Care": random.choice(["Hypertension follow-up", "Diabetes management", "Annual physical", "Cold/flu symptoms", "Medication refill"]),
                    "Pediatrics": random.choice(["Well-child visit", "Immunizations", "Ear infection", "Asthma follow-up", "Sports physical"]),
                    "Behavioral Health": random.choice(["Anxiety management", "Depression follow-up", "Medication management", "Initial intake assessment"]),
                    "Physical Therapy": random.choice(["Post-surgical rehab", "Lower back pain", "Sports injury recovery", "Balance/fall prevention"]),
                    "Urgent Care Walk-In": random.choice(["Laceration", "Minor fracture eval", "Acute respiratory infection", "Sprain/strain", "Fever eval"]),
                    "Lab & Imaging": random.choice(["Routine bloodwork", "X-ray order", "Imaging follow-up", "Pre-op labs"]),
                }[dept_name]

                enc_start = scheduled_dt
                enc_end = enc_start + timedelta(minutes=random.choice([15, 20, 30, 45, 60]))
                encounters.append((enc_id, patient_id, provider_id, dept_id, encounter_class,
                                    enc_start.strftime("%Y-%m-%d %H:%M"), enc_end.strftime("%Y-%m-%d %H:%M"), reason))
                encounter_id = enc_id

                key = (patient_id, dept_name)
                patient_dept_history.setdefault(key, []).append(enc_end)
                enc_id += 1

            appointments.append((appt_id, patient_id, provider_id, dept_id, scheduled_dt.strftime("%Y-%m-%d %H:%M"),
                                  appt_type, status, encounter_id))
            appt_id += 1

    cur.executemany("INSERT INTO appointments VALUES (?,?,?,?,?,?,?,?)", appointments)
    cur.executemany("INSERT INTO encounters VALUES (?,?,?,?,?,?,?,?)", encounters)

    sla_targets = {
        "1 - Critical": (15, 1),
        "2 - High": (60, 8),
        "3 - Moderate": (240, 24),
        "4 - Low": (480, 48),
    }

    tickets_raw = [
        ("INC0010001", "Abel Tuter", "Software", "1 - Critical", "Clinical Applications Support (Tier 2)", "Resolved", "EHR unavailable clinic-wide - providers unable to access patient charts", 42),
        ("INC0010002", "Abraham Lincoln", "Software", "3 - Moderate", "Clinical Applications Support (Tier 2)", "In Progress", "Provider unable to complete order entry in EHR - errors on submit", None),
        ("INC0010003", "Adela Cervantsz", "Inquiry / Help", "4 - Low", "Service Desk (Tier 1)", "Closed", "Password reset needed - locked out of workstation login", 35),
        ("INC0010004", "Aileen Mottern", "Inquiry / Help", "3 - Moderate", "Service Desk (Tier 1)", "Resolved", "Account locked out after repeated failed login attempts", 55),
        ("INC0010005", "Alejandra Prenatt", "Inquiry / Help", "4 - Low", "IAM & Account Support", "In Progress", "New hire needs elevated EHR access provisioned before start date", None),
        ("INC0010006", "Alejandro Mascall", "Hardware", "3 - Moderate", "Desktop & Hardware Support", "New", "Printer offline in Exam Room 3 - unable to print visit summaries", None),
        ("INC0010007", "Alene Rabeck", "Network", "3 - Moderate", "Network & Infrastructure", "Resolved", "VPN not connecting for remote billing staff", 380),
        ("INC0010008", "Alfonso Griglen", "Network", "2 - High", "Network & Infrastructure", "Closed", "Satellite clinic WiFi outage - all staff at South Valley location offline", 340),
        ("INC0010009", "Allie Pumphrey", "Hardware", "3 - Moderate", "Desktop & Hardware Support", "New", "Badge reader malfunctioning at front desk - staff unable to clock in", None),
        ("INC0010010", "Allyson Gillispie", "Software", "2 - High", "Clinical Applications Support (Tier 2)", "In Progress", "e-Prescribing errors for physician - prescriptions failing to transmit to pharmacy", None),
        ("INC0010011", "Alva Pennigton", "Hardware", "3 - Moderate", "Desktop & Hardware Support", "Resolved", "Mobile COW (computer on wheels) won't boot on nursing floor", 1750),
        ("INC0010012", "Alyssa Biasotti", "Inquiry / Help", "2 - High", "IAM & Account Support", "Resolved", "MFA push notification not working for physician logging into Okta", 28),
    ]

    opened_dt = datetime(2026, 7, 29, 8, 0)
    tickets = []
    for number, caller, category, priority, group, state, desc, resolve_minutes in tickets_raw:
        resp_target, res_target_hrs = sla_targets[priority]
        opened = opened_dt + timedelta(minutes=random.randint(0, 180))
        resolved = None
        if resolve_minutes is not None:
            resolved = (opened + timedelta(minutes=resolve_minutes)).strftime("%Y-%m-%d %H:%M")
        tickets.append((number, caller, category, priority, group, state, desc,
                         opened.strftime("%Y-%m-%d %H:%M"), resolved, resp_target, res_target_hrs))

    cur.executemany("INSERT INTO tickets VALUES (?,?,?,?,?,?,?,?,?,?,?)", tickets)

    conn.commit()

    for table in ["patients", "departments", "providers", "appointments", "encounters", "tickets"]:
        n = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: {n} rows")

    conn.close()


if __name__ == "__main__":
    main()
