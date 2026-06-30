import unittest

from backend.auth.services import AuthService, AuthUser, Role, require_role


class AuthServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = AuthService()

    def test_register_and_login_produce_jwt_token(self):
        created = self.service.register_user(
            username="teacher1",
            password="StrongPass123",
            email="teacher@example.com",
            role=Role.TEACHER,
            full_name="Ayşe Yılmaz",
        )

        self.assertTrue(created["success"])
        logged_in = self.service.login_user("teacher1", "StrongPass123")

        self.assertTrue(logged_in["success"])
        self.assertIn("token", logged_in["data"])
        self.assertEqual(logged_in["data"]["user"]["role"], Role.TEACHER)

    def test_non_admin_cannot_access_admin_scope(self):
        self.service.register_user(
            username="teacher2",
            password="StrongPass123",
            email="teacher2@example.com",
            role=Role.TEACHER,
            full_name="Ali Demir",
        )

        user = self.service.authenticate_user("teacher2", "StrongPass123")
        self.assertFalse(require_role(user, [Role.SYSTEM_ADMIN]))

    def test_token_payload_contains_expected_claims(self):
        self.service.register_user(
            username="admin1",
            password="StrongPass123",
            email="admin@example.com",
            role=Role.SYSTEM_ADMIN,
            full_name="Admin User",
        )

        token = self.service.login_user("admin1", "StrongPass123")["data"]["token"]
        payload = self.service.decode_token(token)

        self.assertEqual(payload["sub"], "admin1")
        self.assertEqual(payload["role"], Role.SYSTEM_ADMIN)


if __name__ == "__main__":
    unittest.main()
