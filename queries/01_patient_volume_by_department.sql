-- Q1: Patient volume by department
-- How many completed encounters did each department handle over the
-- ~6-month window, and what share of total clinic volume does that represent?

SELECT
    d.name                                   AS department,
    COUNT(e.encounter_id)                    AS completed_encounters,
    ROUND(100.0 * COUNT(e.encounter_id) / (SELECT COUNT(*) FROM encounters), 1) AS pct_of_total_volume
FROM encounters e
JOIN departments d ON d.department_id = e.department_id
GROUP BY d.name
ORDER BY completed_encounters DESC;
