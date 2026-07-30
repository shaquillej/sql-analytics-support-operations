-- Q6: Average resolution time by priority (Project 2 ticket data)
-- How long, on average, does it actually take to resolve a ticket at each
-- priority tier — and how does that compare to the SLA target?

SELECT
    priority,
    resolution_target_hours,
    COUNT(*)                                                                          AS resolved_or_closed_tickets,
    ROUND(AVG((julianday(resolved_at) - julianday(opened_at)) * 24), 2)                AS avg_resolution_hours
FROM tickets
WHERE state IN ('Resolved', 'Closed')
GROUP BY priority, resolution_target_hours
ORDER BY priority;
