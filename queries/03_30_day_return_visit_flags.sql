-- Q3: 30-day return-visit flags (readmission-style analysis for an outpatient clinic)
-- Wasatch Family Health Clinic is an outpatient family clinic network, not a
-- hospital, so there's no inpatient discharge to re-admit from. The closest
-- real operational equivalent — and a metric outpatient/ambulatory quality
-- teams actually track — is the 30-day return-visit rate: how often a
-- patient comes back to the SAME department within 30 days of a prior visit,
-- which can flag unresolved issues, complications, or scheduling/access
-- problems worth investigating.
--
-- This query self-joins the encounters table to each patient's own
-- encounter history in the same department and flags any visit that
-- occurred within 30 days of an earlier one.

WITH ordered_visits AS (
    SELECT
        e.encounter_id,
        e.patient_id,
        e.department_id,
        e.start_datetime,
        LAG(e.start_datetime) OVER (
            PARTITION BY e.patient_id, e.department_id
            ORDER BY e.start_datetime
        ) AS prior_visit_datetime
    FROM encounters e
)
SELECT
    d.name                                                      AS department,
    COUNT(*)                                                     AS total_encounters,
    SUM(CASE
            WHEN prior_visit_datetime IS NOT NULL
             AND julianday(start_datetime) - julianday(prior_visit_datetime) <= 30
            THEN 1 ELSE 0
        END)                                                     AS return_visits_within_30_days,
    ROUND(100.0 * SUM(CASE
            WHEN prior_visit_datetime IS NOT NULL
             AND julianday(start_datetime) - julianday(prior_visit_datetime) <= 30
            THEN 1 ELSE 0
        END) / COUNT(*), 1)                                       AS return_visit_rate_pct
FROM ordered_visits ov
JOIN departments d ON d.department_id = ov.department_id
GROUP BY d.name
ORDER BY return_visit_rate_pct DESC;
