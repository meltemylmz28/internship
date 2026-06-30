import os
import tempfile
import unittest

from backend.documents.services import DocumentGenerationService


class DocumentGenerationServiceTests(unittest.TestCase):
    def test_generate_document_creates_output_files(self):
        service = DocumentGenerationService(output_dir=tempfile.gettempdir())
        result = service.generate_document(
            template_name="Kulüp Yıllık Çalışma Planı",
            filled_data={"club_name": "Yeşilay Kulübü", "teacher_name": "Ayşe Yılmaz"},
            document_type="docx",
        )

        self.assertTrue(result["success"])
        self.assertTrue(os.path.exists(result["data"]["file_path"]))
        self.assertIn(".docx", result["data"]["file_path"])

    def test_generate_document_supports_pdf_output(self):
        service = DocumentGenerationService(output_dir=tempfile.gettempdir())
        result = service.generate_document(
            template_name="Veli Toplantısı Daveti",
            filled_data={"club_name": "Rehberlik Kulübü", "teacher_name": "Ayşe Yılmaz"},
            document_type="pdf",
        )

        self.assertTrue(result["success"])
        self.assertTrue(os.path.exists(result["data"]["file_path"]))
        self.assertIn(".pdf", result["data"]["file_path"])


if __name__ == "__main__":
    unittest.main()
