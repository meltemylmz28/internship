# Backend scaffold

Bu klasör, MEB uyumlu öğretmen evrak ve plan otomasyonu MVP'sinin ilk adımı için hazırlanmış temel backend yapısını içerir.

## Klasör yapısı
- `backend/education/models.py`: temel domain modelleri
- `backend/education/__init__.py`: eğitim alanı paketi
- `tests/test_backend_models.py`: model davranışlarını doğrulayan testler

## İçerik
- `TeacherProfile` / `User`
- `CurriculumItem` / `Curriculum`
- `TeacherPlan`
- `DocumentTemplate`
- `GeneratedDocument`
