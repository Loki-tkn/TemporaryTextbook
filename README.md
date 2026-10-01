# TemporaryTextbook 📚

> **Authorized Educational Bridge for Missing Textbooks**  
> A simple, compliant MVP web platform connecting students awaiting official textbook shipments with teacher-created and openly licensed bridging study materials.

---

## 🌟 Concept & Compliance Policy

- **The Problem**: Students often experience delays (shipping backorders, campus bookstore stockouts, voucher processing) in receiving their required course textbooks.
- **The Solution**: Students register a missing textbook request. Teachers/Admins approve the request and issue a secure, time-limited **Temporary Access Code** (e.g., `A7K2-P9MX`). Students unlock authorized teacher-authored notes, lecture summaries, and homework exercise sheets.
- **🛡️ Copyright & Distribution Notice**: TemporaryTextbook is an authorized temporary bridge and does **NOT** host or distribute unauthorized scans or copyrighted copies of textbooks. Only teacher-created, school-approved, or openly licensed (CC/OER/MIT) resources are utilized.

---

## 🚀 Tech Stack

- **Backend**: Python 3, FastAPI, SQLAlchemy
- **Database**: SQLite (local embedded database)
- **Frontend / Templating**: Jinja2, Vanilla CSS (Modern design with responsive cards, badges, modal dialogs), Vanilla JavaScript
- **Storage**: Local filesystem storage (`app/static/uploads/`)

---

## 💻 Quick Start & Running Locally

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Web Application
```bash
python -m uvicorn app.main:app --reload
```

### 3. Open in Browser
Visit: **`http://127.0.0.1:8000`**

---

## 🧪 Interactive Demo Walkthrough

The application starts with pre-seeded sample data so you can test every step of the lifecycle right away:

### Complete Lifecycle Demo Steps:

1. **Step 1: Student Requests Textbook**
   - Navigate to `http://127.0.0.1:8000/student`
   - Scroll to **"Request Temporary Access"**
   - Fill in student details:
     - Name: `Alice Smith`
     - Student ID: `STU-1001`
     - Class: `Grade 10B`
     - Subject: `Physics`
     - Reason: `Bookstore out of stock`
   - Click **"Submit Textbook Request"**.

2. **Step 2: Admin / Teacher Approves & Issues Code**
   - Navigate to `http://127.0.0.1:8000/admin`
   - Under the **"Student Requests"** tab, locate Alice Smith's pending request.
   - Click **"✓ Approve & Issue Code"**.
   - Choose validity (e.g. `7 Days`) and click **"Generate Code & Grant Access"**.
   - An access code (formatted `XXXX-XXXX`) is automatically generated with an expiration date.

3. **Step 3: Student Looks Up Code & Accesses Materials**
   - Return to `http://127.0.0.1:8000/student`
   - In **"Check Request Status & Code"**, enter `STU-1001` and click **"Lookup"**.
   - See the approved status and the generated access code.
   - Click **"⚡ Use Code Now to Unlock Materials"** (or enter code in the top access box).
   - Authorized physics formula guides and lab exercises appear immediately with **"Download"** and **"View Online"** options.

4. **Step 4: Expiration & Revocation Security Check**
   - In Admin portal under **"Access Codes"**, click **"Revoke"** next to any active code, or test the pre-seeded expired code `EXP1-9999` and revoked code `RVK8-4444`.
   - When entering an expired or revoked code in the Student Portal, access is immediately blocked with a clear notice.

5. **Step 5: Uploading New Teacher Materials**
   - In Admin portal, click **"Upload Material"**.
   - Fill in Title, Subject, Author, License type, and upload a file (PDF, TXT, DOCX, etc.).
   - The file is stored safely in `app/static/uploads/` and available to students with active codes for that subject.

6. **Resetting Demo Data**
   - Click **"🔄 Reset Demo Data"** at the top of the Admin portal at any time to restore the initial test state.

---

## 📂 Project Structure

```
TemporaryTextbook/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI routes and API endpoints
│   ├── database.py            # SQLite & SQLAlchemy engine setup
│   ├── models.py              # TextbookRequest, AccessCode, Material models
│   ├── schemas.py             # Pydantic schemas for data validation
│   ├── seed_data.py           # Pre-seeded sample records & files
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css      # Clean, modern, responsive styling
│   │   ├── js/
│   │   │   └── app.js         # Interactive AJAX & UI handling
│   │   └── uploads/           # Local storage for teacher materials
│   └── templates/
│       ├── base.html          # Shared layout & disclaimer banner
│       ├── index.html         # Landing page & overview
│       ├── student.html       # Student request & code unlock portal
│       └── admin.html         # Teacher/Admin dashboard & uploads
├── requirements.txt
└── README.md
```

---

## 📜 License
Educational MVP Prototype - Designed for academic continuity and compliant learning bridge operations.
