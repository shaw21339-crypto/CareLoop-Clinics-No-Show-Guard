-- Task 2.4 — Month-by-month trend (4 marks)
-- With a CTE named monthly (month = SUBSTR(appt_date,1,7)), compute appointments and no_show_pct per month, then use LAG() with OVER (ORDER BY month) to show the change in 
-- percentage points — this month's rate minus the previous month's rate (blank for January).

-- Solution
-- Month-by-month trend

WITH monthly AS (
    SELECT
        SUBSTR(appt_date, 1, 7) AS month,
        COUNT(*) AS appointments,
        SUM(no_show) AS no_shows,
        ROUND(
            SUM(no_show) * 100.0 / COUNT(*),
            1
        ) AS no_show_pct
    FROM appointments
    GROUP BY SUBSTR(appt_date, 1, 7)
)

SELECT
    month,
    appointments,
    no_show_pct,
    ROUND(
        no_show_pct -
        LAG(no_show_pct) OVER (ORDER BY month),
        1
    ) AS change_pp
FROM monthly
ORDER BY month;
