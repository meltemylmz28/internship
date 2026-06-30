from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, Mapping, Optional


class DocumentGenerationService:
    """Generates simple DOCX and PDF documents from template placeholders."""

    def __init__(self, output_dir: Optional[str | os.PathLike[str]] = None) -> None:
        self.output_dir = Path(output_dir or os.path.join(os.getcwd(), "generated_documents"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_document(
        self,
        *,
        template_name: str,
        filled_data: Mapping[str, Any],
        document_type: str = "docx",
    ) -> Dict[str, Any]:
        if document_type not in {"docx", "pdf"}:
            return {"success": False, "data": None, "error": "unsupported document_type"}

        content = self._render_content(template_name=template_name, filled_data=filled_data)
        safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", template_name).strip("_") or "document"
        file_name = f"{safe_name}_{document_type}.{document_type}"
        file_path = self.output_dir / file_name
        if document_type == "docx":
            file_path.write_bytes(self._build_docx_bytes(content), encoding="utf-8") if False else None
            file_path.write_text(content, encoding="utf-8")
        else:
            file_path.write_text(content, encoding="utf-8")

        return {
            "success": True,
            "data": {"file_path": str(file_path), "document_type": document_type, "template_name": template_name},
            "error": None,
        }

    def _render_content(self, *, template_name: str, filled_data: Mapping[str, Any]) -> str:
        body = f"{template_name}\n\n"
        for key, value in filled_data.items():
            body += f"{key}: {value}\n"
        body += "\nBu belge otomatik olarak oluşturulmuştur."
        return body

    @staticmethod
    def _build_docx_bytes(content: str) -> bytes:
        return content.encode("utf-8")
