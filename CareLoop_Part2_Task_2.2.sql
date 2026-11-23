-- CareLoop Clinics
-- Task 2.2: No-show rate by clinic
-- Task 2.2 — No-show rate by clinic (5 marks)
-- JOIN appointments to clinics; for each clinic show clinic_name, city, appointments, no_shows and no_show_pct, where no_show_pct is 
-- ROUND(100.0 * SUM(no_show) / COUNT(*), 1). Keep only clinics with at least 95 appointments (HAVING) and sort by no_show_pct descending.
--  Then remove the HAVING line, look at all 8 clinics, and note which clinic has the highest rate and how many appointments it has.
--  In Python, reproduce the clinic counts and no-show counts with groupby and confirm they match the SQL.

-- Solution
-- Step 1: Write the SQL query in MySQL Workbench
SELECT
    c.clinic_name,
    c.city,
    COUNT(*) AS appointments,
    SUM(a.no_show) AS no_shows,
    ROUND(
        100.0 * SUM(a.no_show) / COUNT(*),
        1
    ) AS no_show_pct

FROM appointments AS a

JOIN clinics AS c
    ON a.clinic_id = c.clinic_id

GROUP BY
    c.clinic_id,
    c.clinic_name,
    c.city

HAVING COUNT(*) >= 85

ORDER BY no_show_pct DESC;

-- Step 2: Check all 8 clinics

SELECT
    c.clinic_name,
    c.city,
    COUNT(*) AS appointments,
    SUM(a.no_show) AS no_shows,
    ROUND(
        100.0 * SUM(a.no_show) / COUNT(*),
        1
    ) AS no_show_pct

FROM appointments AS a

JOIN clinics AS c
    ON a.clinic_id = c.clinic_id

GROUP BY
    c.clinic_id,
    c.clinic_name,
    c.city

ORDER BY no_show_pct DESC;