-- Task 2.3 — Does booking far ahead matter? (4 marks)
-- Using CASE WHEN, put lead_days into four bands (the labels must come out of the CASE WHEN, not be typed into the data) — 1-7, 8-14, 15-30, 31+
--  (upper limits inclusive: 7, 14 and 30 belong to the lower band) — and show appointments, no-shows and no_show_pct per band in band order (hint: ORDER BY MIN(lead_days)
--  sorts the bands by how short their lead times are, whereas sorting by the band text would put 15-30 before 8-14).

-- Solution
-- Does booking far ahead matter?
WITH booking_bands AS (
    SELECT
        lead_days,
        no_show,
        CASE
            WHEN lead_days BETWEEN 1 AND 7 THEN '1-7'
            WHEN lead_days BETWEEN 8 AND 14 THEN '8-14'
            WHEN lead_days BETWEEN 15 AND 30 THEN '15-30'
            WHEN lead_days >= 31 THEN '31+'
        END AS lead_band
    FROM appointments
    WHERE lead_days >= 1
)

SELECT
    lead_band,
    COUNT(*) AS appointments,
    SUM(no_show) AS no_shows,
    ROUND(
        SUM(no_show) * 100.0 / COUNT(*), 1
    ) AS no_show_pct
FROM booking_bands
GROUP BY lead_band
ORDER BY MIN(lead_days);