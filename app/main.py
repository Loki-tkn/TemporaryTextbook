import os
import uuid
import datetime
from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File, Form, status
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import engine, get_db, Base
from app.models import TextbookRequest, AccessCode, Material
from app.schemas import (
    TextbookRequestCreate, TextbookRequestResponse,
    ApproveRequestInput, RejectRequestInput,
    RevokeCodeInput, ExtendCodeInput,
    ValidateCodeInput, CodeVerificationResponse, MaterialResponse
)
from app.seed_data import generate_access_code, seed_demo_data, UPLOAD_DIR

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TemporaryTextbook",
    description="Authorized Bridging Educational Access Platform for Missing Textbooks",
    version="1.0.0"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Initialize Jinja2 Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.on_event("startup")
def startup_event():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # Seed initial demo data
    with Session(engine) as db:
        seed_demo_data(db, force=False)


# ====================================================================
# HTML PAGE ROUTES
# ====================================================================

@app.get("/", response_class=HTMLResponse)
def page_home(request: Request, db: Session = Depends(get_db)):
    # Calculate stats
    pending_count = db.query(TextbookRequest).filter(TextbookRequest.status == "Pending").count()
    now = datetime.datetime.utcnow()
    active_codes_count = db.query(AccessCode).filter(
        AccessCode.status == "Active",
        AccessCode.expires_at > now
    ).count()
    materials_count = db.query(Material).count()

    stats = {
        "pending_requests": pending_count,
        "active_codes": active_codes_count,
        "total_materials": materials_count
    }

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "active_page": "home",
            "stats": stats
        }
    )


@app.get("/student", response_class=HTMLResponse)
def page_student(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="student.html",
        context={
            "active_page": "student"
        }
    )


@app.get("/admin", response_class=HTMLResponse)
def page_admin(request: Request, db: Session = Depends(get_db)):
    requests_list = db.query(TextbookRequest).order_by(TextbookRequest.created_at.desc()).all()
    codes_list = db.query(AccessCode).order_by(AccessCode.created_at.desc()).all()
    materials_list = db.query(Material).order_by(Material.created_at.desc()).all()

    now = datetime.datetime.utcnow()
    pending_count = sum(1 for r in requests_list if r.status == "Pending")
    active_codes = sum(1 for c in codes_list if c.current_status == "Active")
    expired_codes = sum(1 for c in codes_list if c.current_status in ("Expired", "Revoked"))

    stats = {
        "pending_requests": pending_count,
        "active_codes": active_codes,
        "expired_codes": expired_codes,
        "total_materials": len(materials_list)
    }

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "active_page": "admin",
            "requests": requests_list,
            "codes": codes_list,
            "materials": materials_list,
            "stats": stats
        }
    )


# ====================================================================
# STUDENT API ENDPOINTS
# ====================================================================

@app.post("/api/requests", response_model=TextbookRequestResponse)
def create_textbook_request(req_in: TextbookRequestCreate, db: Session = Depends(get_db)):
    """Submit a new missing textbook request from a student."""
    new_req = TextbookRequest(
        student_name=req_in.student_name,
        student_id=req_in.student_id,
        class_grade=req_in.class_grade,
        subject=req_in.subject,
        textbook_title=req_in.textbook_title,
        reason=req_in.reason,
        status="Pending"
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)
    return new_req


@app.get("/api/student/status")
def get_student_status(query: str, db: Session = Depends(get_db)):
    """Look up all requests for a student by Student ID or Name."""
    query = query.strip()
    requests = db.query(TextbookRequest).filter(
        (TextbookRequest.student_id.ilike(f"%{query}%")) |
        (TextbookRequest.student_name.ilike(f"%{query}%"))
    ).order_by(TextbookRequest.created_at.desc()).all()

    result = []
    for r in requests:
        # Find latest access code if approved
        code_obj = db.query(AccessCode).filter(AccessCode.request_id == r.id).order_by(AccessCode.created_at.desc()).first()
        result.append({
            "id": r.id,
            "student_name": r.student_name,
            "student_id": r.student_id,
            "class_grade": r.class_grade,
            "subject": r.subject,
            "textbook_title": r.textbook_title,
            "reason": r.reason,
            "status": r.status,
            "admin_note": r.admin_note,
            "created_at": r.created_at.isoformat(),
            "access_code": code_obj.code if code_obj else None,
            "expires_at": code_obj.expires_at.isoformat() if code_obj else None,
            "code_status": code_obj.current_status if code_obj else None
        })

    return {"requests": result}


@app.post("/api/codes/verify", response_model=CodeVerificationResponse)
def verify_access_code(payload: ValidateCodeInput, db: Session = Depends(get_db)):
    """Validate a student's access code and return authorized materials."""
    code_str = payload.code.strip().upper()
    code_record = db.query(AccessCode).filter(AccessCode.code == code_str).first()

    if not code_record:
        return CodeVerificationResponse(
            valid=False,
            message="Invalid Access Code. Please check the code or contact your teacher."
        )

    # Check revocation
    if code_record.status == "Revoked":
        reason = f" ({code_record.revoked_reason})" if code_record.revoked_reason else ""
        return CodeVerificationResponse(
            valid=False,
            status="Revoked",
            message=f"This access code was revoked by the instructor{reason}."
        )

    # Check expiration
    if datetime.datetime.utcnow() > code_record.expires_at:
        return CodeVerificationResponse(
            valid=False,
            status="Expired",
            expires_at=code_record.expires_at,
            message=f"This access code expired on {code_record.expires_at.strftime('%Y-%m-%d %H:%M UTC')}. Please request an extension if textbook is still delayed."
        )

    # Active valid code! Fetch matching subject materials
    materials = db.query(Material).filter(
        Material.subject.ilike(code_record.subject)
    ).order_by(Material.created_at.desc()).all()

    return CodeVerificationResponse(
        valid=True,
        message="Code verified successfully. Authorized learning materials loaded.",
        code=code_record.code,
        student_name=code_record.student_name,
        student_id=code_record.student_id,
        subject=code_record.subject,
        status="Active",
        expires_at=code_record.expires_at,
        materials=[MaterialResponse.model_validate(m) for m in materials]
    )


# ====================================================================
# ADMIN API ENDPOINTS
# ====================================================================

@app.post("/api/admin/requests/approve")
def approve_request(payload: ApproveRequestInput, db: Session = Depends(get_db)):
    """Approve a student's request and generate an access code."""
    req = db.query(TextbookRequest).filter(TextbookRequest.id == payload.request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    # Generate unique access code
    code = payload.custom_code or generate_access_code()
    # Check uniqueness
    while db.query(AccessCode).filter(AccessCode.code == code).first() is not None:
        code = generate_access_code()

    now = datetime.datetime.utcnow()
    expires_at = now + datetime.timedelta(days=payload.duration_days)

    req.status = "Approved"
    if payload.admin_note:
        req.admin_note = payload.admin_note

    access_code = AccessCode(
        code=code,
        student_name=req.student_name,
        student_id=req.student_id,
        subject=req.subject,
        status="Active",
        created_at=now,
        expires_at=expires_at,
        request_id=req.id
    )

    db.add(access_code)
    db.commit()
    db.refresh(access_code)

    return {
        "success": True,
        "message": f"Request #{req.id} approved successfully",
        "code": access_code.code,
        "expires_at": access_code.expires_at.isoformat()
    }


@app.post("/api/admin/requests/reject")
def reject_request(payload: RejectRequestInput, db: Session = Depends(get_db)):
    """Reject a student's missing textbook request."""
    req = db.query(TextbookRequest).filter(TextbookRequest.id == payload.request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    req.status = "Rejected"
    if payload.admin_note:
        req.admin_note = payload.admin_note
    db.commit()

    return {"success": True, "message": f"Request #{req.id} marked as Rejected"}


@app.post("/api/admin/codes/revoke")
def revoke_code(payload: RevokeCodeInput, db: Session = Depends(get_db)):
    """Revoke an active access code."""
    code_record = db.query(AccessCode).filter(AccessCode.code == payload.code.strip().upper()).first()
    if not code_record:
        raise HTTPException(status_code=404, detail="Access code not found")

    code_record.status = "Revoked"
    code_record.revoked_reason = payload.reason or "Revoked by instructor"
    db.commit()

    return {"success": True, "message": f"Code {code_record.code} has been revoked."}


@app.post("/api/admin/codes/extend")
def extend_code(payload: ExtendCodeInput, db: Session = Depends(get_db)):
    """Extend the expiration date for an access code."""
    code_record = db.query(AccessCode).filter(AccessCode.code == payload.code.strip().upper()).first()
    if not code_record:
        raise HTTPException(status_code=404, detail="Access code not found")

    now = datetime.datetime.utcnow()
    # If expired or in past, extend from now; otherwise extend from current expiration
    base_time = code_record.expires_at if code_record.expires_at > now else now
    code_record.expires_at = base_time + datetime.timedelta(days=payload.additional_days)
    code_record.status = "Active"
    code_record.revoked_reason = None
    db.commit()

    return {
        "success": True,
        "message": f"Code {code_record.code} extended to {code_record.expires_at.strftime('%Y-%m-%d %H:%M')}",
        "new_expiration": code_record.expires_at.isoformat()
    }


@app.post("/api/admin/materials/upload")
async def upload_material_file(
    title: str = Form(...),
    subject: str = Form(...),
    author: str = Form(...),
    license_type: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload authorized learning material locally."""
    # Determine extension and safe filename
    orig_name = file.filename or "material.txt"
    ext = os.path.splitext(orig_name)[1].lower()
    clean_stem = "".join(c for c in os.path.splitext(orig_name)[0] if c.isalnum() or c in ("-", "_"))
    saved_filename = f"{clean_stem}_{uuid.uuid4().hex[:8]}{ext}"
    dest_path = os.path.join(UPLOAD_DIR, saved_filename)

    # Save file locally
    contents = await file.read()
    with open(dest_path, "wb") as f:
        f.write(contents)

    file_size_kb = round(len(contents) / 1024, 2)
    file_type_map = {
        ".pdf": "PDF",
        ".docx": "DOCX",
        ".doc": "DOC",
        ".txt": "Notes",
        ".png": "Image",
        ".jpg": "Image",
        ".jpeg": "Image"
    }
    file_type = file_type_map.get(ext, "File")

    mat = Material(
        title=title.strip(),
        subject=subject.strip(),
        description=description.strip() if description else None,
        file_name=saved_filename,
        original_filename=orig_name,
        file_type=file_type,
        file_size_kb=file_size_kb,
        author=author.strip(),
        license_type=license_type.strip()
    )
    db.add(mat)
    db.commit()
    db.refresh(mat)

    return {
        "success": True,
        "id": mat.id,
        "title": mat.title,
        "subject": mat.subject,
        "file_name": mat.file_name
    }


@app.delete("/api/admin/materials/{material_id}")
def delete_material(material_id: int, db: Session = Depends(get_db)):
    """Delete a material and remove its local file."""
    mat = db.query(Material).filter(Material.id == material_id).first()
    if not mat:
        raise HTTPException(status_code=404, detail="Material not found")

    file_path = os.path.join(UPLOAD_DIR, mat.file_name)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass

    db.delete(mat)
    db.commit()

    return {"success": True, "message": f"Material '{mat.title}' deleted"}


@app.post("/api/admin/seed-demo")
def reset_seed_demo(db: Session = Depends(get_db)):
    """Reset database to initial sample demo data."""
    seed_demo_data(db, force=True)
    return {"success": True, "message": "Demo data successfully re-seeded."}


# ====================================================================
# FILE ACCESS & DOWNLOAD ENDPOINTS
# ====================================================================

@app.get("/api/materials/{material_id}/download")
def download_material_file(material_id: int, code: Optional[str] = None, db: Session = Depends(get_db)):
    """Download material file with code authorization check."""
    mat = db.query(Material).filter(Material.id == material_id).first()
    if not mat:
        raise HTTPException(status_code=404, detail="Material not found")

    # If student provided code, verify authorization
    if code:
        code_obj = db.query(AccessCode).filter(AccessCode.code == code.strip().upper()).first()
        if not code_obj or not code_obj.is_valid:
            raise HTTPException(status_code=403, detail="Invalid or expired access code.")

    file_path = os.path.join(UPLOAD_DIR, mat.file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server disk.")

    return FileResponse(
        path=file_path,
        filename=mat.original_filename,
        media_type="application/octet-stream"
    )


@app.get("/api/materials/{material_id}/view")
def view_material_file(material_id: int, code: Optional[str] = None, db: Session = Depends(get_db)):
    """View material file in browser."""
    mat = db.query(Material).filter(Material.id == material_id).first()
    if not mat:
        raise HTTPException(status_code=404, detail="Material not found")

    if code:
        code_obj = db.query(AccessCode).filter(AccessCode.code == code.strip().upper()).first()
        if not code_obj or not code_obj.is_valid:
            raise HTTPException(status_code=403, detail="Invalid or expired access code.")

    file_path = os.path.join(UPLOAD_DIR, mat.file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server disk.")

    # Determine media type for inline viewing
    ext = os.path.splitext(mat.file_name)[1].lower()
    media_map = {
        ".pdf": "application/pdf",
        ".txt": "text/plain; charset=utf-8",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg"
    }
    media_type = media_map.get(ext, "application/octet-stream")

    return FileResponse(
        path=file_path,
        media_type=media_type
    )
