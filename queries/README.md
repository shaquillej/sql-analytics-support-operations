# Query Notes — Wasatch Family Health Clinic SQL Analytics

Six queries, run against `wasatch_clinic_ops.db` (SQLite). The first three analyze the clinic's own appointment/encounter data; the last three analyze the service desk ticket data reused from [Project 2](https://github.com/shaquillej/servicenow-healthcare-it-service-desk). Results below are from the seeded dataset in this repo — re-running `generate_data.py` with the same seed reproduces them exactly.

## Q1 — Patient volume by department (`01_patient_volume_by_department.sql`)

**Question:** How many completed encounters did each department handle, and what share of total clinic volume does that represent?

| Department | Completed Encounters | % of Total Volume |
|---|---|---|
| Primary Care | 516 | 23.1% |
| Urgent Care Walk-In | 444 | 19.9% |
| Pediatrics | 413 | 18.5% |
| Lab & Imaging | 399 | 17.9% |
| Physical Therapy | 234 | 10.5% |
| Behavioral Health | 229 | 10.2% |

Primary Care carries the largest share of volume, consistent with its role as the clinic's front door for most patients — as expected for a family health clinic network.

## Q2 — No-show rate by department (`02_no_show_rate_by_department.sql`)

**Question:** What share of scheduled appointments in each department end in a no-show, versus completed or cancelled?

| Department | Scheduled | Completed | No-Shows | Cancelled | No-Show Rate |
|---|---|---|---|---|---|
| Behavioral Health | 296 | 229 | 53 | 14 | 17.9% |
| Physical Therapy | 315 | 234 | 56 | 25 | 17.8% |
| Primary Care | 603 | 516 | 51 | 36 | 8.5% |
| Pediatrics | 461 | 413 | 26 | 22 | 5.6% |
| Urgent Care Walk-In | 497 | 444 | 19 | 34 | 3.8% |
| Lab & Imaging | 442 | 399 | 17 | 26 | 3.8% |

Behavioral Health and Physical Therapy run the highest no-show rates by a wide margin — a well-documented pattern in outpatient care (recurring appointments, stigma/avoidance for behavioral health, and pain-related avoidance for PT). This is where a clinic would prioritize reminder-call or telehealth-option investment.

## Q3 — 30-day return-visit flags (`03_30_day_return_visit_flags.sql`)

**Question:** How often does a patient return to the same department within 30 days of a prior visit?

Wasatch Family Health Clinic is an outpatient network, not a hospital, so there's no inpatient discharge to measure a classic "readmission" against. The closest real operational equivalent — and a metric ambulatory quality teams actually track — is the **30-day return-visit rate**, which can flag unresolved issues, complications, or access problems.

| Department | Total Encounters | Return Visits (≤30 days) | Return-Visit Rate |
|---|---|---|---|
| Primary Care | 516 | 149 | 28.9% |
| Urgent Care Walk-In | 444 | 107 | 24.1% |
| Pediatrics | 413 | 99 | 24.0% |
| Lab & Imaging | 399 | 75 | 18.8% |
| Physical Therapy | 234 | 35 | 15.0% |
| Behavioral Health | 229 | 28 | 12.2% |

Primary Care's high return-visit rate is expected — it's the department that manages chronic conditions (hypertension, diabetes) with frequent follow-up by design, not a quality flag on its own. This is exactly why the query reports the rate per department rather than a single clinic-wide number: the "right" rate is different for a chronic-disease-management department than for one-off urgent care visits, and a real analyst would need that context before treating any single number as good or bad.

## Q4 — Ticket volume by category (`04_ticket_volume_by_category.sql`)

**Question:** Which incident categories are driving the most service desk volume?

| Category | Tickets | % of Total |
|---|---|---|
| Inquiry / Help | 4 | 33.3% |
| Software | 3 | 25.0% |
| Hardware | 3 | 25.0% |
| Network | 2 | 16.7% |

With only 12 tickets in the Project 2 dataset this is a small sample, but it matches the design intent of that project: password resets and account/access requests (Inquiry/Help) are the highest-volume, lowest-complexity Tier 1 category — the textbook case for knowledge-base deflection, which is exactly what Project 2's 6 KB articles targeted.

## Q5 — SLA compliance rate (`05_sla_compliance_rate.sql`)

**Question:** Of the tickets that reached Resolved or Closed, what share hit their Priority-based resolution target?

| Priority | Resolved/Closed | Met SLA | Compliance Rate |
|---|---|---|---|
| 1 - Critical | 1 | 1 | 100.0% |
| 2 - High | 2 | 2 | 100.0% |
| 3 - Moderate | 3 | 2 | 66.7% |
| 4 - Low | 1 | 1 | 100.0% |

The one miss is INC0010011 (mobile workstation wouldn't boot) — a spare unit was swapped in immediately for the nurse to keep working, but the ticket itself stayed open past the 24-hour Moderate target while the original unit was queued for hardware repair. That's a realistic SLA miss: the *user* was unblocked fast, but the *ticket* — measured strictly against the clock — still breached, which is exactly the kind of gap between "user impact resolved" and "SLA met" that a real service desk metric review would need to explain.

## Q6 — Average resolution time by priority (`06_avg_resolution_time_by_priority.sql`)

**Question:** How long does it actually take to resolve a ticket at each priority tier, compared to the SLA target?

| Priority | SLA Target (hrs) | Resolved/Closed | Avg. Resolution (hrs) |
|---|---|---|---|
| 1 - Critical | 1 | 1 | 0.70 |
| 2 - High | 8 | 2 | 3.07 |
| 3 - Moderate | 24 | 3 | 12.14 |
| 4 - Low | 48 | 1 | 0.58 |

Average resolution time sits comfortably under target for every tier except where the single Moderate-priority miss (INC0010011) pulls the average up — which is also why Q5 and Q6 are reported side by side: an average can look fine even when a specific ticket breached, so both the rate and the average are needed to see the full picture.
