-- Task 2.1 — Build and load the database (4 marks)

-- In MySQL Workbench run CREATE DATABASE noshowguard; USE noshowguard; (skip in SQLiteOnline).
 Create the two tables below, then run your load_data.sql:

-- CREATE TABLE clinics (
--   clinic_id VARCHAR(5) PRIMARY KEY, clinic_name VARCHAR(40) NOT NULL, city VARCHAR(20) NOT NULL,
--   tier VARCHAR(10), latitude DECIMAL(8,4), longitude DECIMAL(8,4), temp_c DECIMAL(5,1));
-- CREATE TABLE appointments (
--   appointment_id VARCHAR(8) PRIMARY KEY, patient_id VARCHAR(8) NOT NULL, clinic_id VARCHAR(5) NOT NULL,
--   booked_on DATE, appt_date DATE, age INT, gender VARCHAR(1), distance_km DECIMAL(5,1), fee_inr INT,
--   booking_channel VARCHAR(10), visit_type VARCHAR(12), reminder_sent VARCHAR(3), prior_no_shows INT,
--   status VARCHAR(10), lead_days INT, no_show INT,
--   FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id));

-- Solution
-- ==========================================
--  CARELOOP CLINICS
--  PART 2 - TASK 2.1
--  Build and load the database
--  ==========================================

Create Database Noshowguard;
Use Noshowguard;

-- Step 1: Create clinics table
CREATE TABLE clinics (
    clinic_id VARCHAR(5) PRIMARY KEY,
    clinic_name VARCHAR(40) NOT NULL,
    city VARCHAR(20) NOT NULL,
    tier VARCHAR(10),
    latitude DECIMAL(8,4),
    longitude DECIMAL(8,4),
    temp_c DECIMAL(5,1)
);

-- Step 2: Create appointments table
CREATE TABLE appointments (
    appointment_id VARCHAR(8) PRIMARY KEY,
    patient_id VARCHAR(8) NOT NULL,
    clinic_id VARCHAR(5) NOT NULL,
    booked_on DATE,
    appt_date DATE,
    age INT,
    gender VARCHAR(1),
    distance_km DECIMAL(5,1),
    fee_inr INT,
    booking_channel VARCHAR(10),
    visit_type VARCHAR(12),
    reminder_sent VARCHAR(3),
    prior_no_shows INT,
    status VARCHAR(10),
    lead_days INT,
    no_show INT,
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id)
);

SELECT COUNT(*) AS total_clinics
FROM clinics;

SELECT COUNT(*) AS total_appointments
FROM appointments;

SELECT SUM(no_show) AS total_no_shows
FROM appointments;

-- Test duplicate appointment ID
INSERT INTO appointments
SELECT *
FROM appointments
WHERE appointment_id = 'A0001'

-- Task 2.2 — No-show rate by clinic (5 marks)

-- JOIN appointments to clinics; for each clinic show clinic_name, city, appointments, no_shows and
--no_show_pct, where no_show_pct is  ROUND(100.0 * SUM(no_show) / COUNT(*), 1). Keep only clinics with at
 -- least 95 appointments (HAVING) and sort by no_show_pct descending.
--  Then remove the HAVING line, look at all 8 clinics, and note which clinic has the highest rate
--and how many appointments it has.
--  In Python, reproduce the clinic counts and no-show counts with groupby and confirm they match the SQL.

-- Solution
-- ==========================================
--  CARELOOP CLINICS
--  PART 2 - TASK 2.2
--  No-show rate by clinic
--  ==========================================

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

-- Task 2.3 — Does booking far ahead matter? (4 marks)

-- Using CASE WHEN, put lead_days into four bands (the labels must come out of the CASE WHEN, not be
-- typed into the data)  —1-7, 8-14, 15-30, 31+ (upper limits inclusive: 7, 14 and 30 belong to the lower
-- band) — and show appointments, no-shows and no_show_pct per band in band order (hint: ORDER BY MIN
-- (lead_days) sorts the bands by how short their  lead times are, whereas sorting by the band text would
--  put 15-30 before 8-14).

-- Solution
-- ==========================================
--  CARELOOP CLINICS
--  PART 2 - TASK 2.3
--  Does booking far ahead matter?
--  ==========================================

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

-- Task 2.4 — Month-by-month trend (4 marks)

-- With a CTE named monthly (month = SUBSTR (appt_date,1,7)), compute appointments and no_show_pct per month, then use
 -- LAG() with OVER (ORDER BY month) to show the change in percentage points — this month's rate minus
-- the previous month's rate (blank for January).

-- Solution
-- ==========================================
--  CARELOOP CLINICS
--  PART 2 - TASK 2.4
--  Month-by-month trend
-- ==========================================

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

-- Task 2.5 — Rank clinics inside each city (5 marks)

-- With a CTE clinic_rates (clinic, city, no_show_pct), select every clinic with RANK() OVER
--(PARTITION BY city ORDER BY no_show_pct DESC) as rank_in_city, plus a column
-- vs_overall that says 'above', 'below' or 'equal' (no clinic is exactly equal here,
-- but the query should handle it) by comparing the clinic's rate with the overall no-show
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
