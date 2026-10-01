import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# Request Schemas
class TextbookRequestCreate(BaseModel):
    student_name: str = Field(..., min_length=2, max_length=100)
    student_id: str = Field(..., min_length=2, max_length=50)
    class_grade: str = Field(..., min_length=1, max_length=50)
    subject: str = Field(..., min_length=2, max_length=100)
    textbook_title: Optional[str] = None
    reason: Optional[str] = None


class TextbookRequestResponse(BaseModel):
    id: int
    student_name: str
    student_id: str
    class_grade: str
    subject: str
    textbook_title: Optional[str]
    reason: Optional[str]
    status: str
    admin_note: Optional[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    access_code: Optional[str] = None
    expires_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True


class ApproveRequestInput(BaseModel):
    request_id: int
    duration_days: int = Field(default=7, ge=1, le=90)
    custom_code: Optional[str] = None
    admin_note: Optional[str] = None


class RejectRequestInput(BaseModel):
    request_id: int
    admin_note: Optional[str] = None


class RevokeCodeInput(BaseModel):
    code: str
    reason: Optional[str] = None


class ExtendCodeInput(BaseModel):
    code: str
    additional_days: int = Field(default=7, ge=1, le=90)


# Code Validation / Material Access
class ValidateCodeInput(BaseModel):
    code: str = Field(..., min_length=4, max_length=20)


class MaterialResponse(BaseModel):
    id: int
    title: str
    subject: str
    description: Optional[str]
    file_name: str
    original_filename: str
    file_type: str
    file_size_kb: float
    author: str
    license_type: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class CodeVerificationResponse(BaseModel):
    valid: bool
    message: str
    code: Optional[str] = None
    student_name: Optional[str] = None
    student_id: Optional[str] = None
    subject: Optional[str] = None
    status: Optional[str] = None
    expires_at: Optional[datetime.datetime] = None
    materials: List[MaterialResponse] = []
