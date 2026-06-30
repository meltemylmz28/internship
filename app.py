from __future__ import annotations

import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from backend.auth.services import AuthService, Role, require_role
from backend.documents.services import DocumentGenerationService
from backend.planning.services import AcademicCalendarService, CurriculumPlannerService
from backend.education.models import CurriculumItem


class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._send_json({"success": True, "data": {"status": "ok"}, "error": None})
            return

        if parsed.path == "/":
            self._send_html(self._read_static("index.html"))
            return

        if parsed.path == "/styles.css":
            self._send_text(self._read_static("styles.css"), content_type="text/css; charset=utf-8")
            return

        if parsed.path == "/app.js":
            self._send_text(self._read_static("app.js"), content_type="application/javascript; charset=utf-8")
            return

        self._send_json({"success": False, "data": None, "error": "not found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        length = self.headers.get("Content-Length")
        body = ""
        if length:
            body = self.rfile.read(int(length)).decode("utf-8")
        else:
            body = self.rfile.read().decode("utf-8")

        if parsed.path == "/api/auth/register":
            payload = self._parse_payload(body, parsed)
            result = self.server.auth_service.register_user_endpoint(payload)
            self._send_json(result)
            return

        if parsed.path == "/api/auth/login":
            payload = self._parse_payload(body, parsed)
            result = self.server.auth_service.login_user_endpoint(payload)
            self._send_json(result)
            return

        if parsed.path == "/api/plans/generate":
            payload = self._parse_payload(body, parsed)
            curriculum_items = payload.get("curriculum_items")
            if isinstance(curriculum_items, str):
                try:
                    payload["curriculum_items"] = json.loads(curriculum_items)
                except json.JSONDecodeError:
                    payload["curriculum_items"] = []
            result = self.server.planner.match_curriculum_endpoint(payload)
            self._send_json(result)
            return

        if parsed.path == "/api/documents/generate":
            payload = self._parse_payload(body, parsed)
            filled_data = payload.get("filled_data", {})
            if isinstance(filled_data, str):
                try:
                    filled_data = json.loads(filled_data)
                except json.JSONDecodeError:
                    filled_data = {}
            result = self.server.document_service.generate_document(
                template_name=str(payload.get("template_name", "Belge")),
                filled_data=filled_data,
                document_type=str(payload.get("document_type", "docx")),
            )
            self._send_json(result)
            return

        self._send_json({"success": False, "data": None, "error": "not found"}, status=404)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return

    def _send_json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, content: str, status: int = 200) -> None:
        self._send_text(content, content_type="text/html; charset=utf-8", status=status)

    def _send_text(self, content: str, content_type: str, status: int = 200) -> None:
        body = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _parse_payload(self, raw_body: str, parsed: object) -> dict:
        query_params = parse_qs(parsed.query, keep_blank_values=True)
        if query_params:
            return {key: values[0] if len(values) == 1 else values for key, values in query_params.items()}

        if not raw_body:
            return {}

        try:
            return json.loads(raw_body)
        except json.JSONDecodeError:
            form_data = parse_qs(raw_body, keep_blank_values=True)
            return {key: values[0] if len(values) == 1 else values for key, values in form_data.items()}

    def _read_static(self, file_name: str) -> str:
        path = self.server.static_dir / file_name
        return path.read_text(encoding="utf-8")


class AppServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], handler_class: type[BaseHTTPRequestHandler], static_dir: str) -> None:
        super().__init__(server_address, handler_class)
        self.static_dir = Path(static_dir)
        self.auth_service = AuthService()
        self.auth_service.seed_demo_user()
        self.planner = CurriculumPlannerService(AcademicCalendarService())
        self.document_service = DocumentGenerationService(output_dir="generated_documents")


def main() -> None:
    host = "127.0.0.1"
    port = 8000
    server = AppServer((host, port), AppHandler, str(Path(__file__).resolve().parent / "static"))
    print(f"Server listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
