from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class TeacherProfile:
    """Represents a teacher user profile for the document automation platform."""

    full_name: str
    role: str = "teacher"
    school_name: Optional[str] = None
    branch: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True

    def __post_init__(self) -> None:
        self.full_name = self.full_name.strip()
        if not self.full_name:
            raise ValueError("full_name is required")
        if not self.role.strip():
            raise ValueError("role is required")


User = TeacherProfile


@dataclass(slots=True)
class CurriculumItem:
    """Represents a single curriculum entry from the MEB curriculum pool."""

    subject: str
    grade_level: str
    unit: str
    week: int
    learning_outcome: str
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.subject.strip():
            raise ValueError("subject is required")
        if not self.grade_level.strip():
            raise ValueError("grade_level is required")
        if not self.unit.strip():
            raise ValueError("unit is required")
        if not self.learning_outcome.strip():
            raise ValueError("learning_outcome is required")
        if self.week < 1:
            raise ValueError("week must be greater than zero")

    def summary(self) -> str:
        return f"{self.subject} / {self.grade_level} / {self.unit} / Hafta {self.week}: {self.learning_outcome}"


Curriculum = CurriculumItem


@dataclass(slots=True)
class TeacherPlan:
    """Represents a teacher's customized plan entry for an academic year."""

    teacher_id: int
    curriculum_item_id: int
    academic_year: str
    notes: str = ""
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if self.teacher_id < 1:
            raise ValueError("teacher_id must be greater than zero")
        if self.curriculum_item_id < 1:
            raise ValueError("curriculum_item_id must be greater than zero")
        if not self.academic_year.strip():
            raise ValueError("academic_year is required")


@dataclass(slots=True)
class DocumentTemplate:
    """Stores the structure of a document template for official paperwork."""

    name: str
    document_type: str
    template_body: str
    dynamic_fields: List[str] = field(default_factory=list)
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name is required")
        if not self.document_type.strip():
            raise ValueError("document_type is required")
        if not self.template_body.strip():
            raise ValueError("template_body is required")

    @property
    def is_dynamic(self) -> bool:
        return bool(self.dynamic_fields)


@dataclass(slots=True)
class GeneratedDocument:
    """Represents a filled document generated for a teacher."""

    teacher_id: int
    template_id: int
    filled_data: Dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if self.teacher_id < 1:
            raise ValueError("teacher_id must be greater than zero")
        if self.template_id < 1:
            raise ValueError("template_id must be greater than zero")

    def to_payload(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "teacher_id": self.teacher_id,
            "template_id": self.template_id,
            "filled_data": dict(self.filled_data),
            "created_at": self.created_at.isoformat(),
        }
