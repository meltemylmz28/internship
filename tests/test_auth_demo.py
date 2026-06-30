import unittest

from backend.auth.services import AuthService, Role


class AuthDemoTests(unittest.TestCase):
    def test_seed_demo_user_registers_default_teacher_account(self):
        service = AuthService()
        service.seed_demo_user()

        user = service.authenticate_user("demo.teacher", "DemoPass123")
        self.assertIsNotNone(user)
        self.assertEqual(user.role, Role.TEACHER)


if __name__ == "__main__":
    unittest.main()
