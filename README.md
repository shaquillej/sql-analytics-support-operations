# SQL Analytics on Support & Operations Data

SQL analysis project for the same fictional healthcare organization used across this portfolio, Wasatch Family Health Clinic — ties clinic operations data together with the ServiceNow ticket data from the companion [Healthcare IT Service Desk Simulation](https://github.com/shaquillej/servicenow-healthcare-it-service-desk) project.

## Overview

This project answers realistic operational questions with SQL: how patient volume breaks down across a clinic's departments, where no-shows and return visits are concentrated, and — reusing the incident data from Project 2 — how well the service desk is actually meeting its SLA targets. Six queries, two data sources, one narrative.

## About the Dataset

**Clinic operations data (patients, providers, appointments, encounters)** is a synthetic dataset generated for this project with a seeded Python script (`generate_data.py`), modeled on the kind of appointment/encounter-level data a clinic's practice-management or EHR system produces — the same category of data MITRE's Synthea patient generator produces, though this dataset was authored directly for this project rather than run through Synthea itself. It covers 220 patients, 6 departments, 18 providers, and roughly 2,600 scheduled appointments over a 6-month window, with realistic department-level variation in volume and no-show rates built in (behavioral health and physical therapy run materially higher no-show rates than primary care or lab/imaging, which matches real-world ambulatory-care patterns).

**Service desk ticket data** is reused as-is from Project 2's 12-incident ServiceNow ticket log, with resolution timestamps reconstructed against each ticket's SLA target (the original ServiceNow simulation tracked ticket state, not full timestamp history) so SLA-compliance and resolution-time queries are possible. One ticket (INC0010011) was deliberately left breaching its SLA target — a real service desk's compliance rate is essentially never a clean 100%, and a query that can only ever return "everything passed" isn't proving much.

## What Was Built

- `schema.sql` — SQLite schema: `patients`, `departments`, `providers`, `appointments`, `encounters`, `tickets`
- `generate_data.py` — seeded synthetic data generator (re-run it to reproduce the exact dataset)
- `data/` — CSV export of every table, for browsing without running the script
- `queries/` — 6 SQL query files plus `queries/README.md` with a plain-language explanation and results table for each one

## The Six Queries

1. Patient volume by department
2. No-show rate by department
3. 30-day return-visit flags (the outpatient-clinic equivalent of a readmission analysis)
4. Ticket volume by category (Project 2 data)
5. SLA compliance rate by priority (Project 2 data)
6. Average resolution time by priority (Project 2 data)

Full explanations and results for each are in [`queries/README.md`](queries/README.md).

## How to Run This

```
python3 generate_data.py        # builds wasatch_clinic_ops.db from schema.sql + seeded data
sqlite3 wasatch_clinic_ops.db < queries/01_patient_volume_by_department.sql
# ...repeat for any query file, or open wasatch_clinic_ops.db in any SQLite client
```

## Tools and Skills Demonstrated

SQL (joins, aggregation, window functions, CTEs, date/time arithmetic), SQLite database design, synthetic healthcare data modeling, and translating operational questions (no-show rates, SLA compliance, resolution time) into queries that produce a defensible, explainable answer — not just a number.

## About

Built by Shaquille Jackson as part of a self-directed transition from healthcare operations into Healthcare IT and IAM. Portfolio: https://shaquillejackson.com
