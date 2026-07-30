-- Q2: No-show rate by department
-- What share of scheduled appointments in each department result in a
-- no-show, versus completed or cancelled? Cancellations are shown separately
-- since a cancellation (with notice) is an operationally different problem
-- than a true no-show (missed slot, no notice).

SELECT
    d.name                                                             AS department,
    COUNT(a.appointment_id)                                            AS total_scheduled,
    SUM(CASE WHEN a.status = 'Completed' THEN 1 ELSE 0 END)            AS completed,
    SUM(CASE WHEN a.status = 'No-Show'   THEN 1 ELSE 0 END)            AS no_shows,
    SUM(CASE WHEN a.status = 'Cancelled' THEN 1 ELSE 0 END)            AS cancelled,
    ROUND(100.0 * SUM(CASE WHEN a.status = 'No-Show' THEN 1 ELSE 0 END) / COUNT(a.appointment_id), 1) AS no_show_rate_pct
FROM appointments a
JOIN departments d ON d.department_id = a.department_id
GROUP BY d.name
ORDER BY no_show_rate_pct DESC;
