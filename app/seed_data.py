import os
import secrets
import datetime
from sqlalchemy.orm import Session
from app.models import TextbookRequest, AccessCode, Material

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")


def generate_access_code() -> str:
    """Generate a clean format access code like A7K2-P9MX"""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    part1 = "".join(secrets.choice(alphabet) for _ in range(4))
    part2 = "".join(secrets.choice(alphabet) for _ in range(4))
    return f"{part1}-{part2}"


def create_sample_files():
    """Create sample teacher-created and openly licensed files in uploads dir."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    sample_files_content = {
        "Math_Week1_Calculus_Summary.txt": """============================================================
TEMPORARY LEARNING MATERIAL - AUTHORIZED BRIDGING RESOURCE
Subject: Mathematics (Calculus I)
Instructor: Prof. Margaret Vance | Dept. of Mathematics
License: School Authorized / Teacher Original Curriculum
Notice: This is a temporary bridging guide while official textbooks arrive.
============================================================

TOPIC 1: LIMITS AND CONTINUITY
------------------------------------------------------------
1. Intuitive Definition of a Limit:
   As x approaches 'c', f(x) approaches 'L', denoted as:
   lim (x -> c) f(x) = L

2. Key Limit Laws:
   - Sum Law: lim [f(x) + g(x)] = lim f(x) + lim g(x)
   - Product Law: lim [f(x) * g(x)] = lim f(x) * lim g(x)
   - Quotient Law: lim [f(x) / g(x)] = lim f(x) / lim g(x) (provided lim g(x) != 0)

3. Continuity Checklist:
   A function f(x) is continuous at x = a if:
   a) f(a) is defined.
   b) lim (x -> a) f(x) exists.
   c) lim (x -> a) f(x) = f(a).

WEEK 1 PRACTICE PROBLEMS:
1. Evaluate lim (x -> 3) (x^2 - 9) / (x - 3)
2. Determine if f(x) = (x^2 - 4)/(x - 2) for x != 2 and f(2) = 4 is continuous at x = 2.
3. Find lim (x -> 0) (sqrt(x + 4) - 2) / x

Homework due on Friday at 5:00 PM via Class Portal.
""",
        "Physics_Mechanics_Formulas_Guide.txt": """============================================================
TEMPORARY LEARNING MATERIAL - FORMULA REFERENCE & LAB GUIDE
Subject: Physics
Instructor: Dr. Alan Turing | Science Faculty
License: CC BY-NC 4.0 (Open Educational Resource)
============================================================

1. KINEMATICS (CONSTANT ACCELERATION):
   - v = v0 + a * t
   - x = x0 + v0 * t + 0.5 * a * t^2
   - v^2 = v0^2 + 2 * a * (x - x0)
   - Average Velocity: v_avg = (v0 + v) / 2

2. NEWTON'S LAWS:
   - First Law (Inertia): An object remains at rest or constant velocity unless acted upon.
   - Second Law: F_net = m * a
   - Third Law: For every action, there is an equal and opposite reaction.
   - Gravitational Force: F_g = m * g (g ≈ 9.81 m/s^2)
   - Kinetic Friction: f_k = μ_k * F_N

3. LAB 1 EXERCISES:
   - Measuring acceleration down an inclined track with photogates.
   - Record 5 trials at 15°, 20°, and 25° angles.
""",
        "ComputerScience_Intro_Python_Notes.txt": """============================================================
TEMPORARY LEARNING MATERIAL - STARTER NOTES & CHEATSHEET
Subject: Computer Science
Instructor: Elena Rostova | Dept. of Computer Science
License: MIT Licensed Educational Material
============================================================

DATA STRUCTURES IN PYTHON:
- Lists: ordered, mutable, [1, 2, 3]
- Tuples: ordered, immutable, (1, 2, 3)
- Dictionaries: key-value pairs, {'name': 'Alice', 'id': 'S101'}
- Sets: unordered, unique elements, {1, 2, 3}

CONTROL FLOW:
for item in collection:
    if condition:
        process(item)
    else:
        fallback()

EXERCISE:
Write a function `filter_even_squares(numbers: list[int]) -> list[int]`
that returns squares of all even numbers.
""",
        "Biology_Cell_Structure_Worksheet.txt": """============================================================
TEMPORARY LEARNING MATERIAL - CELL BIOLOGY STUDY COMPANION
Subject: Biology
Instructor: Dr. Richard Owens | Life Sciences
License: School Open Curriculum
============================================================

CELL ORGANELLES & FUNCTIONS:
1. Nucleus: Houses genetic material (DNA); controls cellular activities.
2. Mitochondria: Powerhouse of the cell; produces ATP via cellular respiration.
3. Ribosomes: Protein synthesis machinery.
4. Endoplasmic Reticulum (ER):
   - Rough ER: Studded with ribosomes; synthesizes and folds proteins.
   - Smooth ER: Lipid synthesis and detoxification.
5. Golgi Apparatus: Modifies, sorts, and packages proteins for transport.
6. Chloroplasts (Plant cells): Photosynthesis site containing chlorophyll.

REVIEW QUESTIONS:
1. Differentiate between prokaryotic and eukaryotic cell membranes.
2. Explain the endosymbiotic theory of mitochondrial evolution.
"""
    }

    for fname, content in sample_files_content.items():
        filepath = os.path.join(UPLOAD_DIR, fname)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip())


def seed_demo_data(db: Session, force: bool = False):
    """Seed the database with rich demo requests, codes, and authorized materials."""
    if not force:
        if db.query(TextbookRequest).first() is not None:
            return  # already seeded

    # Clear existing if force
    if force:
        db.query(AccessCode).delete()
        db.query(TextbookRequest).delete()
        db.query(Material).delete()
        db.commit()

    create_sample_files()
    now = datetime.datetime.utcnow()

    # 1. Seed Materials (Openly licensed/teacher authored)
    materials = [
        Material(
            title="Week 1-2 Calculus Notes & Problem Set",
            subject="Mathematics",
            description="Teacher-compiled lecture notes on Limits, Continuity, and foundational exercises.",
            file_name="Math_Week1_Calculus_Summary.txt",
            original_filename="Calculus_Week1_Limits_Summary.txt",
            file_type="Notes",
            file_size_kb=3.2,
            author="Prof. Margaret Vance",
            license_type="Teacher Original Curriculum",
            created_at=now - datetime.timedelta(days=3)
        ),
        Material(
            title="Physics Mechanics Formula & Lab Guide",
            subject="Physics",
            description="Core kinematic equations, Newton's Laws reference sheet, and Lab 1 procedures.",
            file_name="Physics_Mechanics_Formulas_Guide.txt",
            original_filename="Physics_Kinematics_Formulas.txt",
            file_type="Notes",
            file_size_kb=2.8,
            author="Dr. Alan Turing",
            license_type="CC BY-NC 4.0 Open Educational Resource",
            created_at=now - datetime.timedelta(days=2)
        ),
        Material(
            title="Python Fundamentals & Syntax Cheatsheet",
            subject="Computer Science",
            description="Official departmental guide covering Python basic structures and homework exercises.",
            file_name="ComputerScience_Intro_Python_Notes.txt",
            original_filename="CS101_Python_Basics.txt",
            file_type="Notes",
            file_size_kb=2.1,
            author="Elena Rostova",
            license_type="MIT Open Curriculum",
            created_at=now - datetime.timedelta(days=1)
        ),
        Material(
            title="Cell Structure & Organelles Study Companion",
            subject="Biology",
            description="Comprehensive organelle diagrams summary, function comparison table, and quiz review.",
            file_name="Biology_Cell_Structure_Worksheet.txt",
            original_filename="Bio_Cell_Structures_Guide.txt",
            file_type="Notes",
            file_size_kb=2.5,
            author="Dr. Richard Owens",
            license_type="School Open Curriculum",
            created_at=now - datetime.timedelta(days=4)
        )
    ]

    for m in materials:
        db.add(m)
    db.commit()

    # 2. Seed Requests & Access Codes
    # Request 1: Approved with Active Code
    req1 = TextbookRequest(
        student_name="Bob Johnson",
        student_id="STU-1002",
        class_grade="Grade 11A",
        subject="Mathematics",
        textbook_title="Stewart Calculus: Early Transcendentals",
        reason="Ordered online textbook, delivery delayed by postal service until next week.",
        status="Approved",
        admin_note="Approved temporary 7-day access to Math week 1-2 teacher notes.",
        created_at=now - datetime.timedelta(days=1, hours=2)
    )
    db.add(req1)
    db.commit()
    db.refresh(req1)

    code1 = AccessCode(
        code="A7K2-P9MX",
        student_name="Bob Johnson",
        student_id="STU-1002",
        subject="Mathematics",
        status="Active",
        created_at=now - datetime.timedelta(days=1),
        expires_at=now + datetime.timedelta(days=6),  # 6 days left
        request_id=req1.id
    )
    db.add(code1)

    # Request 2: Pending Request
    req2 = TextbookRequest(
        student_name="Alice Smith",
        student_id="STU-1001",
        class_grade="Grade 10B",
        subject="Physics",
        textbook_title="University Physics with Modern Physics",
        reason="Bookstore ran out of stock on campus. Waiting for backorder replenishment.",
        status="Pending",
        admin_note=None,
        created_at=now - datetime.timedelta(hours=4)
    )
    db.add(req2)

    # Request 3: Expired Code Request
    req3 = TextbookRequest(
        student_name="Charlie Brown",
        student_id="STU-1003",
        class_grade="Grade 12C",
        subject="Computer Science",
        textbook_title="Introduction to Algorithms & Python",
        reason="Awaiting international parcel delivery.",
        status="Approved",
        admin_note="Temporary 5-day code granted.",
        created_at=now - datetime.timedelta(days=10)
    )
    db.add(req3)
    db.commit()
    db.refresh(req3)

    code3 = AccessCode(
        code="EXP1-9999",
        student_name="Charlie Brown",
        student_id="STU-1003",
        subject="Computer Science",
        status="Active",  # will evaluate as Expired because expires_at is in the past
        created_at=now - datetime.timedelta(days=10),
        expires_at=now - datetime.timedelta(days=3),  # expired 3 days ago
        request_id=req3.id
    )
    db.add(code3)

    # Request 4: Revoked Code Request
    req4 = TextbookRequest(
        student_name="Diana Prince",
        student_id="STU-1004",
        class_grade="Grade 10A",
        subject="Biology",
        textbook_title="Campbell Biology 12th Ed",
        reason="Forgot book at home during transition.",
        status="Approved",
        admin_note="Code revoked as student received physical copy from library reserve.",
        created_at=now - datetime.timedelta(days=5)
    )
    db.add(req4)
    db.commit()
    db.refresh(req4)

    code4 = AccessCode(
        code="RVK8-4444",
        student_name="Diana Prince",
        student_id="STU-1004",
        subject="Biology",
        status="Revoked",
        created_at=now - datetime.timedelta(days=5),
        expires_at=now + datetime.timedelta(days=2),
        revoked_reason="Student picked up physical library reserve copy.",
        request_id=req4.id
    )
    db.add(code4)

    # Request 5: Another Pending Request
    req5 = TextbookRequest(
        student_name="Evan Davis",
        student_id="STU-1005",
        class_grade="Grade 11B",
        subject="Computer Science",
        textbook_title="Python Data Structures & OOP",
        reason="New transfer student; textbook voucher processing.",
        status="Pending",
        admin_note=None,
        created_at=now - datetime.timedelta(hours=1)
    )
    db.add(req5)

    db.commit()
