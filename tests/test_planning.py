import unittest

from backend.education.models import CurriculumItem
from backend.planning.services import AcademicCalendarService, CurriculumPlannerService


class PlanningServiceTests(unittest.TestCase):
    def test_calendar_marks_holiday_weeks(self):
        service = AcademicCalendarService()
        calendar = service.build_calendar("2025-2026")

        self.assertGreaterEqual(len(calendar["weeks"]), 36)
        self.assertTrue(any(week["is_holiday_week"] for week in calendar["weeks"]))

    def test_curriculum_planner_matches_items_to_weeks(self):
        planner = CurriculumPlannerService(AcademicCalendarService())
        curriculum_items = [
            CurriculumItem(subject="Matematik", grade_level="6", unit="Kesirler", week=1, learning_outcome="Kesirleri tanır."),
            CurriculumItem(subject="Matematik", grade_level="6", unit="Oran", week=2, learning_outcome="Oran kavramını açıklar."),
        ]

        plan = planner.build_yearly_plan(
            curriculum_items=curriculum_items,
            academic_year="2025-2026",
            subject="Matematik",
            grade_level="6",
            weeks_limit=4,
        )

        self.assertEqual(len(plan["weeks"]), 4)
        self.assertTrue(any(entry["curriculum_item"] for entry in plan["weeks"]))
        self.assertIn("Matematik", plan["weeks"][0]["curriculum_item"])


if __name__ == "__main__":
    unittest.main()
