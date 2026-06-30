from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence

from backend.education.models import CurriculumItem


class AcademicCalendarService:
    """Builds a lightweight academic calendar with holiday-aware weeks."""

    def build_calendar(self, academic_year: str) -> Dict[str, Any]:
        start_year = int(academic_year.split("-")[0])
        start_date = date(start_year, 9, 1)
        weeks: List[Dict[str, Any]] = []
        for week_number in range(1, 41):
            week_start = start_date + timedelta(days=(week_number - 1) * 7)
            week_end = week_start + timedelta(days=6)
            holiday_names = self._holiday_names_for_week(academic_year, week_start, week_end)
            weeks.append(
                {
                    "week_number": week_number,
                    "start_date": week_start.isoformat(),
                    "end_date": week_end.isoformat(),
                    "holiday_names": holiday_names,
                    "is_holiday_week": bool(holiday_names),
                }
            )

        return {"academic_year": academic_year, "weeks": weeks, "total_weeks": len(weeks)}

    def _holiday_names_for_week(self, academic_year: str, week_start: date, week_end: date) -> List[str]:
        holidays = self._holidays_for_year(academic_year)
        return [name for name, holiday_date in holidays.items() if week_start <= holiday_date <= week_end]

    def _holidays_for_year(self, academic_year: str) -> Dict[str, date]:
        year_prefix = int(academic_year.split("-")[0])
        year_suffix = int(academic_year.split("-")[1])
        if academic_year == "2025-2026":
            return {
                "Yılbaşı": date(2026, 1, 1),
                "Ramazan Bayramı": date(2026, 3, 21),
                "Milli Mücadele": date(2025, 10, 29),
            }
        if academic_year == "2024-2025":
            return {
                "Yılbaşı": date(2025, 1, 1),
                "Milli Mücadele": date(2024, 10, 29),
            }
        return {
            "Yılbaşı": date(year_suffix, 1, 1),
            "Milli Mücadele": date(year_prefix, 10, 29),
        }


class CurriculumPlannerService:
    """Matches curriculum items to weekly plan slots and exposes a planning endpoint payload."""

    def __init__(self, calendar_service: Optional[AcademicCalendarService] = None) -> None:
        self.calendar_service = calendar_service or AcademicCalendarService()

    def build_yearly_plan(
        self,
        *,
        curriculum_items: Sequence[CurriculumItem],
        academic_year: str,
        subject: str,
        grade_level: str,
        weeks_limit: int = 36,
    ) -> Dict[str, Any]:
        calendar = self.calendar_service.build_calendar(academic_year)
        filtered_items = [
            item for item in curriculum_items if item.subject == subject and item.grade_level == grade_level
        ]
        filtered_items.sort(key=lambda item: (item.week, item.unit))

        weeks = []
        for index, week in enumerate(calendar["weeks"][:weeks_limit]):
            if week["is_holiday_week"]:
                weeks.append({**week, "curriculum_item": None, "status": "holiday"})
                continue
            curriculum_item = None
            if filtered_items:
                curriculum_item = filtered_items[index % len(filtered_items)].summary()
            weeks.append({**week, "curriculum_item": curriculum_item, "status": "planned"})

        return {
            "academic_year": academic_year,
            "subject": subject,
            "grade_level": grade_level,
            "weeks": weeks,
            "matched_items_count": len(filtered_items),
        }

    def match_curriculum_endpoint(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        curriculum_items = [
            CurriculumItem(
                subject=str(item.get("subject", "")).strip(),
                grade_level=str(item.get("grade_level", "")).strip(),
                unit=str(item.get("unit", "")).strip(),
                week=int(item.get("week", 1)),
                learning_outcome=str(item.get("learning_outcome", "")).strip(),
            )
            for item in payload.get("curriculum_items", [])
        ]
        plan = self.build_yearly_plan(
            curriculum_items=curriculum_items,
            academic_year=str(payload.get("academic_year", "2025-2026")).strip(),
            subject=str(payload.get("subject", "")).strip(),
            grade_level=str(payload.get("grade_level", "")).strip(),
            weeks_limit=int(payload.get("weeks_limit", 36)),
        )
        return {"success": True, "data": plan, "error": None}
