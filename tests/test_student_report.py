import os
import tempfile
import unittest

from student_report import evaluate_student, generate_report, load_students


class StudentReportTests(unittest.TestCase):
    def test_evaluate_student_returns_praise_when_all_selected_fields_are_filled(self):
        student = {"student_name": "Ali", "matematik": "85", "fen": "90", "ingilizce": "88"}
        result = evaluate_student(student, ["matematik", "fen", "ingilizce"])

        self.assertEqual(result["status"], "ovgu")
        self.assertEqual(result["missing_features"], [])
        self.assertIn("övgü", result["message"].lower())

    def test_evaluate_student_returns_warning_when_some_fields_are_missing(self):
        student = {"student_name": "Ayşe", "matematik": "78", "fen": "", "ingilizce": "84"}
        result = evaluate_student(student, ["matematik", "fen", "ingilizce"])

        self.assertEqual(result["status"], "iyimser_uyari")
        self.assertEqual(result["missing_features"], ["fen"])
        self.assertIn("iyimser", result["message"].lower())

    def test_generate_report_reads_csv_and_outputs_results(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as handle:
            handle.write("student_name,matematik,fen,ingilizce\n")
            handle.write("Ali,85,90,88\n")
            handle.write("Ayşe,78,,84\n")
            temp_path = handle.name

        try:
            students = load_students(temp_path)
            results = generate_report(students, ["matematik", "fen", "ingilizce"])
        finally:
            os.remove(temp_path)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["status"], "ovgu")
        self.assertEqual(results[1]["status"], "iyimser_uyari")


if __name__ == "__main__":
    unittest.main()
