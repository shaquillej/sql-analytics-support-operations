-- Q5: SLA compliance rate (resolved/closed tickets from Project 2)
-- Of the tickets that reached Resolved or Closed, what share hit their
-- Priority-based resolution target from the SLA matrix?
-- (New / In Progress tickets are excluded — they haven't reached a
-- resolution outcome yet, so they can't be scored as met/missed.)

SELECT
    priority,
    COUNT(*)                                                                          AS resolved_or_closed_tickets,
    SUM(CASE
            WHEN (julianday(resolved_at) - julianday(opened_at)) * 24 <= resolution_target_hours
            THEN 1 ELSE 0
        END)                                                                           AS met_sla,
    ROUND(100.0 * SUM(CASE
            WHEN (julianday(resolved_at) - julianday(opened_at)) * 24 <= resolution_target_hours
            THEN 1 ELSE 0
        END) / COUNT(*), 1)                                                            AS sla_compliance_pct
FROM tickets
WHERE state IN ('Resolved', 'Closed')
GROUP BY priority
ORDER BY priority;
