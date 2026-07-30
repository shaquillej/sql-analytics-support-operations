-- Q4: Ticket volume by category (from Project 2's ServiceNow ticket log)
-- Which incident categories are driving the most service desk volume?

SELECT
    category,
    COUNT(*)                                                            AS ticket_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM tickets), 1)         AS pct_of_total
FROM tickets
GROUP BY category
ORDER BY ticket_count DESC;
