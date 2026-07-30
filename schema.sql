-- Wasatch Family Health Clinic -- Support & Operations Data
-- SQLite schema for Project 3 (SQL Analytics)

DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS providers;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS encounters;
DROP TABLE IF EXISTS tickets;

CREATE TABLE patients (
      patient_id      INTEGER PRIMARY KEY,
      first_name      TEXT NOT NULL,
      last_name       TEXT NOT NULL,
      dob             TEXT NOT NULL,      -- YYYY-MM-DD
    gender          TEXT NOT NULL       -- 'F' / 'M'
);

CREATE TABLE departments (
      department_id   INTEGER PRIMARY KEY,
      name            TEXT NOT NULL,
      specialty       TEXT NOT NULL
  );

CREATE TABLE providers (
      provider_id     INTEGER PRIMARY KEY,
      name            TEXT NOT NULL,
      specialty       TEXT NOT NULL,
      department_id   INTEGER NOT NULL REFERENCES departments(department_id)
  );

-- Every scheduled visit, whether or not it happened
CREATE TABLE appointments (
      appointment_id  INTEGER PRIMARY KEY,
      patient_id      INTEGER NOT NULL REFERENCES patients(patient_id),
      provider_id     INTEGER NOT NULL REFERENCES providers(provider_id),
      department_id   INTEGER NOT NULL REFERENCES departments(department_id),
      scheduled_date  TEXT NOT NULL,      -- YYYY-MM-DD HH:MM
    appointment_type TEXT NOT NULL,
      status          TEXT NOT NULL,      -- 'Completed' / 'No-Show' / 'Cancelled'
    encounter_id    INTEGER REFERENCES encounters(encounter_id)  -- set only when status = 'Completed'
);

-- The clinical visit record created when an appointment is completed
CREATE TABLE encounters (
      encounter_id    INTEGER PRIMARY KEY,
      patient_id      INTEGER NOT NULL REFERENCES patients(patient_id),
      provider_id     INTEGER NOT NULL REFERENCES providers(provider_id),
      department_id   INTEGER NOT NULL REFERENCES departments(department_id),
      encounter_class TEXT NOT NULL,      -- 'ambulatory' / 'wellness' / 'urgent' / 'emergency'
    start_datetime  TEXT NOT NULL,
      end_datetime    TEXT NOT NULL,
      reason          TEXT NOT NULL
  );

-- Service desk tickets, reused from Project 2 (ServiceNow simulation)
CREATE TABLE tickets (
      ticket_number       TEXT PRIMARY KEY,
      caller               TEXT NOT NULL,
      category              TEXT NOT NULL,
      priority              TEXT NOT NULL,
      assignment_group      TEXT NOT NULL,
      state                 TEXT NOT NULL,
      short_description     TEXT NOT NULL,
      opened_at             TEXT NOT NULL,
      resolved_at           TEXT,              -- NULL if still open (New / In Progress)
    response_target_minutes  INTEGER NOT NULL,
      resolution_target_hours  INTEGER NOT NULL
  );
