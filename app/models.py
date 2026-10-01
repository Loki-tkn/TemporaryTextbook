import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.database import Base


class TextbookRequest(Base):
    __tablename__ = "textbook_requests"

    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String(100), nullable=False)
    student_id = Column(String(50), nullable=False, index=True)
    class_grade = Column(String(50), nullable=False)
    subject = Column(String(100), nullable=False, index=True)
    textbook_title = Column(String(200), nullable=True)
    reason = Column(Text, nullable=True)
    status = Column(String(20), default="Pending", index=True)  # Pending, Approved, Rejected
    admin_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    access_codes = relationship("AccessCode", back_populates="request", cascade="all, delete-orphan")


class AccessCode(Base):
    __tablename__ = "access_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    student_name = Column(String(100), nullable=False)
    student_id = Column(String(50), nullable=False, index=True)
    subject = Column(String(100), nullable=False, index=True)
    status = Column(String(20), default="Active", index=True)  # Active, Expired, Revoked
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    revoked_reason = Column(String(200), nullable=True)

    request_id = Column(Integer, ForeignKey("textbook_requests.id", ondelete="SET NULL"), nullable=True)
    request = relationship("TextbookRequest", back_populates="access_codes")

    @property
    def current_status(self) -> str:
        """Dynamically evaluate status based on revocation and expiration time."""
        if self.status == "Revoked":
            return "Revoked"
        if datetime.datetime.utcnow() > self.expires_at:
            return "Expired"
        return "Active"

    @property
    def is_valid(self) -> bool:
        return self.current_status == "Active"


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    subject = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    file_name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # PDF, DOCX, Image, Text
    file_size_kb = Column(Float, default=0.0)
    author = Column(String(100), default="Course Instructor")
    license_type = Column(String(100), default="Authorized School Material / OER")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
