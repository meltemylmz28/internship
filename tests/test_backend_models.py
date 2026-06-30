import unittest

from backend.education.models import (
    CurriculumItem,
    DocumentTemplate,
    GeneratedDocument,
    TeacherPlan,
    TeacherProfile,
)


class BackendModelsTests(unittest.TestCase):
    def test_teacher_profile_requires_full_name_and_role(self):
        teacher = TeacherProfile(full_name="Ayşe Yılmaz", role="teacher", school_name="Atatürk Ortaokulu")

        self.assertEqual(teacher.full_name, "Ayşe Yılmaz")
        self.assertEqual(teacher.role, "teacher")
        self.assertTrue(teacher.is_active)

    def test_curriculum_item_builds_a_summary(self):
        curriculum_item = CurriculumItem(
            subject="Matematik",
            grade_level="6",
            unit="Kesirler",
            week=3,
            learning_outcome="Kesirleri karşılaştırır.",
        )

        self.assertIn("Matematik", curriculum_item.summary())
        self.assertIn("Kesirler", curriculum_item.summary())

    def test_teacher_plan_uses_academic_year_and_notes(self):
        plan = TeacherPlan(
            teacher_id=1,
            curriculum_item_id=7,
            academic_year="2025-2026",
            notes="Hafta sonu tekrar yapılacak.",
        )

        self.assertEqual(plan.academic_year, "2025-2026")
        self.assertIn("Hafta sonu", plan.notes)

    def test_document_template_extracts_dynamic_fields(self):
        template = DocumentTemplate(
            name="Kulüp Yıllık Çalışma Planı",
            document_type="club_plan",
            template_body="{{club_name}} için {{teacher_name}} tarafından hazırlanmıştır.",
            dynamic_fields=["club_name", "teacher_name"],
        )

        self.assertEqual(template.dynamic_fields, ["club_name", "teacher_name"])
        self.assertTrue(template.is_dynamic)

    def test_generated_document_serializes_payload(self):
        document = GeneratedDocument(
            teacher_id=1,
            template_id=2,
            filled_data={"club_name": "Yeşilay Kulübü", "teacher_name": "Ayşe Yılmaz"},
        )

        payload = document.to_payload()
        self.assertEqual(payload["teacher_id"], 1)
        self.assertEqual(payload["filled_data"]["club_name"], "Yeşilay Kulübü")


if __name__ == "__main__":
    unittest.main()
