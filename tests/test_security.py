"""Unit tests for SOUNDARYA 3-Tier Security and Permission Architecture."""

import unittest
from app.core.state import ActionRequest, PermissionLevel
from app.core.security import security_engine


class TestSecurityEngine(unittest.TestCase):
    def test_level_1_safe_action(self) -> None:
        req = ActionRequest(
            action_id="act-1",
            action_name="app:open",
            category="app",
            parameters={"app_name": "Calculator"}
        )
        is_authorized, reason = security_engine.validate_and_authorize(req)
        self.assertTrue(is_authorized)
        self.assertIsNone(reason)
        self.assertEqual(req.permission_level, PermissionLevel.LEVEL_1)

    def test_level_2_confirmation_denied(self) -> None:
        security_engine.register_confirmation_handler(lambda r: False)

        req = ActionRequest(
            action_id="act-2",
            action_name="file:delete",
            category="file",
            parameters={"path": "/tmp/test.txt"}
        )
        is_authorized, reason = security_engine.validate_and_authorize(req)
        self.assertFalse(is_authorized)
        self.assertIn("cancelled by user", reason or "")
        self.assertEqual(req.permission_level, PermissionLevel.LEVEL_2)

    def test_level_2_confirmation_accepted(self) -> None:
        security_engine.register_confirmation_handler(lambda r: True)

        req = ActionRequest(
            action_id="act-3",
            action_name="memory:clear_all",
            category="memory"
        )
        is_authorized, reason = security_engine.validate_and_authorize(req)
        self.assertTrue(is_authorized)
        self.assertTrue(req.confirmed)

    def test_level_3_restricted_strictly_blocked(self) -> None:
        req = ActionRequest(
            action_id="act-4",
            action_name="system:shutdown_force",
            category="system"
        )
        is_authorized, reason = security_engine.validate_and_authorize(req)
        self.assertFalse(is_authorized)
        self.assertIn("RESTRICTED", reason or "")
        self.assertEqual(req.permission_level, PermissionLevel.LEVEL_3)


if __name__ == "__main__":
    unittest.main()
