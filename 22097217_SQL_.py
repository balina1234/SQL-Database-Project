"""
University Database System – SQLite Implementation

This project develops a relational university database using SQLite.
The system represents academic structures including faculties, academic
programmes, student records, modules, module offerings, registrations,
and examination results.

The database contains more than 1000 student records and demonstrates
realistic institutional relationships through foreign keys and composite
(primary compound) keys.

All data has been synthetically generated for academic purposes.

DATA TYPES INCLUDED:

Nominal data (categorical, no order):
    - Students.gender
    - Faculties.faculty_name
    - Programs.program_name
    - Modules.module_name

Ordinal data (categorical with order):
    - Students.study_level
        (Foundation < Undergraduate < Postgraduate < PhD)
    - Results.grade_band
        (Pass < Merit < Distinction)

Interval data (numeric scale with arbitrary zero):
    - Students.date_of_birth
        (date → difference meaningful, zero meaningless)
    - Registrations.registration_date
        (calendar date → no true zero)

Ratio data (numeric with true zero):
    - Modules.credit_value
    - Students.tuition_fee
    - Module_Offerings.capacity
    - Results.marks

KEYS:

Foreign Keys:
    - Programs.faculty_id → Faculties.faculty_id
    - Students.program_id → Programs.program_id
    - Module_Offerings.module_id → Modules.module_id
    - Registrations.student_id → Students.student_id
    - Registrations.module_id → Modules.module_id

Composite (Compound) Keys:
    - Module_Offerings(module_id, academic_year, term)
    - Registrations(student_id, module_id, academic_year, term)
    - Results(student_id, module_id, academic_year, term)

DATA REALISM FEATURES:

- 3% missing tuition_fee values intentionally inserted
- 2% duplicate student names intentionally introduced
- Randomized but realistic credit values and tuition ranges
- Multi-year academic offerings (2022–2024)
- Referential integrity enforced using foreign key constraints

All data has been programmatically generated using the Faker library.
No real student data has been used.
"""
"""
University Database System – SQLite Implementation

This database models university operations including faculties, programs,
students, modules, registrations and results.

Measurement Types:
-------------------------------------
Nominal  → categorical, no order
Ordinal  → categorical, ordered
Interval → date/time, no true zero
Ratio    → numeric, true zero

All data is synthetically generated for academic purposes.
"""


# IMPORTS
from faker import Faker
import sqlite3
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# SETUP
fake = Faker()
Faker.seed(55)
random.seed(55)
np.random.seed(55)

DB_PATH = "university_database_system.db"


# SUPPORT FUNCTIONS (INTERVAL)
def random_birthdate():
    start = datetime(1990,1,1)
    end = datetime(2006,12,31)
    delta = end - start
    return (start + timedelta(days=random.randint(0,delta.days))).date().isoformat()

def random_registration_date():
    start = datetime(2021,1,1)
    end = datetime(2024,12,31)
    delta = end - start
    return (start + timedelta(days=random.randint(0,delta.days))).date().isoformat()


# 1. FACULTIES (Nominal)
faculties_df = pd.DataFrame([
    {"faculty_id":1, "faculty_name":"Engineering"},
    {"faculty_id":2, "faculty_name":"Business"},
    {"faculty_id":3, "faculty_name":"Science"},
    {"faculty_id":4, "faculty_name":"Arts"},
    {"faculty_id":5, "faculty_name":"Health Sciences"}
])


# 2. PROGRAMS (Nominal + FK)
programs = []

for pid in range(1,21):
    programs.append({
        "program_id": pid,
        "program_name": fake.word().capitalize() + " Studies",  # Nominal
        "faculty_id": random.randint(1,5)
    })

programs_df = pd.DataFrame(programs)


# 3. STUDENTS (1000 rows)

study_levels = ["Foundation","Undergraduate","Postgraduate","PhD"]  # Ordinal

students = []

for sid in range(1,1001):
    students.append({
        "student_id": sid,
        "student_name": fake.name(),  # Nominal
        "gender": random.choice(["Male","Female","Other"]),  # Nominal
        "date_of_birth": random_birthdate(),  # Interval
        "study_level": random.choice(study_levels),  # Ordinal
        "tuition_fee": round(random.uniform(5000,20000),2),  # Ratio
        "program_id": random.randint(1,20)
    })

students_df = pd.DataFrame(students)

# Inject 3% missing tuition_fee
missing_idx = np.random.choice(
    students_df.index,
    size=int(0.03*len(students_df)),
    replace=False
)
students_df.loc[missing_idx,"tuition_fee"] = None

# Inject 2% duplicate names
dup_idx = np.random.choice(
    students_df.index,
    size=int(0.02*len(students_df)),
    replace=False
)

for idx in dup_idx:
    sample = students_df.sample(1).iloc[0]
    students_df.at[idx,"student_name"] = sample["student_name"]


# 4. MODULES (Ratio)
modules = []

for mid in range(1,101):
    modules.append({
        "module_id": mid,
        "module_name": fake.word().capitalize(),
        "credit_value": random.choice([15,20,30])  # Ratio
    })

modules_df = pd.DataFrame(modules)


# 5. MODULE_OFFERINGS (Composite PK)
offerings = []

for year in range(2022,2025):
    for term in ["Semester1","Semester2"]:
        for _, module in modules_df.iterrows():
            if random.random() < 0.5:
                offerings.append({
                    "module_id": module["module_id"],
                    "academic_year": year,
                    "term": term,
                    "capacity": random.randint(30,200)  # Ratio
                })

offerings_df = pd.DataFrame(offerings)


# 6. REGISTRATIONS (Composite PK)
registrations = []

for _ in range(2000):
    student = students_df.sample(1).iloc[0]
    offering = offerings_df.sample(1).iloc[0]

    registrations.append({
        "student_id": student["student_id"],
        "module_id": offering["module_id"],
        "academic_year": offering["academic_year"],
        "term": offering["term"],
        "registration_date": random_registration_date()  # Interval
    })

registrations_df = pd.DataFrame(registrations).drop_duplicates(
    subset=["student_id","module_id","academic_year","term"]
)


# 7. RESULTS
grade_bands = ["Pass","Merit","Distinction"]  # Ordinal

results = []

for _, row in registrations_df.sample(frac=0.8).iterrows():
    results.append({
        "student_id": row["student_id"],
        "module_id": row["module_id"],
        "academic_year": row["academic_year"],
        "term": row["term"],
        "marks": random.randint(40,100),  # Ratio
        "grade_band": random.choice(grade_bands)  # Ordinal
    })

results_df = pd.DataFrame(results)

# CREATE DATABASE
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

schema = """
CREATE TABLE Faculties(
    faculty_id INTEGER PRIMARY KEY,
    faculty_name TEXT
);

CREATE TABLE Programs(
    program_id INTEGER PRIMARY KEY,
    program_name TEXT,
    faculty_id INTEGER,
    FOREIGN KEY(faculty_id) REFERENCES Faculties(faculty_id)
);

CREATE TABLE Students(
    student_id INTEGER PRIMARY KEY,
    student_name TEXT,
    gender TEXT,
    date_of_birth TEXT,
    study_level TEXT,
    tuition_fee REAL,
    program_id INTEGER,
    FOREIGN KEY(program_id) REFERENCES Programs(program_id)
);

CREATE TABLE Modules(
    module_id INTEGER PRIMARY KEY,
    module_name TEXT,
    credit_value INTEGER
);

CREATE TABLE Module_Offerings(
    module_id INTEGER,
    academic_year INTEGER,
    term TEXT,
    capacity INTEGER,
    PRIMARY KEY(module_id, academic_year, term),
    FOREIGN KEY(module_id) REFERENCES Modules(module_id)
);

CREATE TABLE Registrations(
    student_id INTEGER,
    module_id INTEGER,
    academic_year INTEGER,
    term TEXT,
    registration_date TEXT,
    PRIMARY KEY(student_id, module_id, academic_year, term),
    FOREIGN KEY(student_id) REFERENCES Students(student_id),
    FOREIGN KEY(module_id) REFERENCES Modules(module_id)
);

CREATE TABLE Results(
    student_id INTEGER,
    module_id INTEGER,
    academic_year INTEGER,
    term TEXT,
    marks INTEGER,
    grade_band TEXT,
    PRIMARY KEY(student_id, module_id, academic_year, term)
);
"""

cur.executescript(schema)
conn.commit()

faculties_df.to_sql("Faculties", conn, if_exists="append", index=False)
programs_df.to_sql("Programs", conn, if_exists="append", index=False)
students_df.to_sql("Students", conn, if_exists="append", index=False)
modules_df.to_sql("Modules", conn, if_exists="append", index=False)
offerings_df.to_sql("Module_Offerings", conn, if_exists="append", index=False)
registrations_df.to_sql("Registrations", conn, if_exists="append", index=False)
results_df.to_sql("Results", conn, if_exists="append", index=False)

conn.commit()
conn.close()

print("University Database System created successfully.")