-- Task 2.1 — Build and load the database (4 marks)
-- In MySQL Workbench run CREATE DATABASE noshowguard; USE noshowguard; (skip in SQLiteOnline). Create the two tables below, then run your load_data.sql:

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
# ==========================================
# CARELOOP CLINICS
# PART 2 - TASK 2.1
# Build and load the database
# ==========================================

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