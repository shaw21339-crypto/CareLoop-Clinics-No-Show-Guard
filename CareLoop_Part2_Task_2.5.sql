-- Task 2.5 — Rank clinics inside each city (5 marks)
-- With a CTE clinic_rates (clinic, city, no_show_pct), select every clinic with RANK() OVER (PARTITION BY city ORDER BY no_show_pct DESC) as rank_in_city, plus a column 
-- vs_overall that says 'above', 'below' or 'equal' (no clinic is exactly equal here, but the query should handle it) by comparing the clinic's rate with the overall no-show 
-- rate computed in a scalar subquery. Order by city, then rank.

-- Solution
-- ==========================================
--  CARELOOP CLINICS
--  PART 2 - TASK 2.5
--  Rank clinics inside each city
--  ==========================================

WITH clinic_rates AS (
    SELECT
        c.clinic_name AS clinic,
        c.city,
        ROUND(
            SUM(a.no_show) * 100.0 / COUNT(*),
            1
        ) AS no_show_pct
    FROM clinics c
    JOIN appointments a
        ON c.clinic_id = a.clinic_id
    GROUP BY
        c.clinic_id,
        c.clinic_name,
        c.city
)

SELECT
    clinic,
    city,
    no_show_pct,

    RANK() OVER (
        PARTITION BY city
        ORDER BY no_show_pct DESC
    ) AS rank_in_city,

    CASE
        WHEN no_show_pct > (
            SELECT SUM(no_show) * 100.0 / COUNT(*)
            FROM appointments
        ) THEN 'above'

        WHEN no_show_pct < (
            SELECT SUM(no_show) * 100.0 / COUNT(*)
            FROM appointments
        ) THEN 'below'

        ELSE 'equal'
    END AS vs_overall

FROM clinic_rates

ORDER BY city, rank_in_city;