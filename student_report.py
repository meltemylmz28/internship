import csv
import json
from pathlib import Path
from typing import Any, Dict, List


def normalize_value(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def load_students(csv_path: str | Path) -> List[Dict[str, str]]:
    with open(csv_path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return [{key: normalize_value(value) for key, value in row.items()} for row in reader]


def evaluate_student(student: Dict[str, str], selected_features: List[str]) -> Dict[str, Any]:
    student_name = student.get("student_name", "Öğrenci") or "Öğrenci"
    missing_features = [feature for feature in selected_features if not student.get(feature, "")]

    if missing_features:
        message = (
            f"{student_name} için eksik veriler mevcut. "
            f"iyimser bir uyarı ile desteklenmiş bir değerlendirme: "
            f"Bu alanlar tamamlandığında performans daha güçlü bir tabloya dönüşebilir."
        )
        return {
            "student_name": student_name,
            "status": "iyimser_uyari",
            "missing_features": missing_features,
            "message": message,
        }

    message = (
        f"{student_name} için seçilen özellikler tamamlanmış. "
        "Yapay zeka destekli değerlendirme: çok güçlü bir ilerleme ve övgüye değer bir profil ortaya çıkıyor."
    )
    return {
        "student_name": student_name,
        "status": "ovgu",
        "missing_features": [],
        "message": message,
    }


def generate_report(students: List[Dict[str, str]], selected_features: List[str]) -> List[Dict[str, Any]]:
    return [evaluate_student(student, selected_features) for student in students]


def save_report(results: List[Dict[str, Any]], output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="MEB karne benzeri verileri işleyip öğrenci değerlendirme raporu üretir")
    parser.add_argument("--input", required=True, help="Girdi CSV dosyası")
    parser.add_argument("--features", required=True, help="Virgülle ayrılmış değerlendirme alanları")
    parser.add_argument("--output", default="report.json", help="Çıktı JSON dosyası")
    args = parser.parse_args()

    selected_features = [feature.strip() for feature in args.features.split(",") if feature.strip()]
    students = load_students(args.input)
    results = generate_report(students, selected_features)
    save_report(results, args.output)

    print(f"{len(results)} öğrenci için rapor üretildi: {args.output}")


if __name__ == "__main__":
    main()
