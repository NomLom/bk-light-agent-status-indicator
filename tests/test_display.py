from __future__ import annotations

import unittest

from agent_status.display import STATE_COLORS


class DisplayColorTests(unittest.TestCase):
    def test_active_states_are_not_black(self) -> None:
        for state in ("thinking", "tool_use", "permission", "success", "failed", "cancelled"):
            self.assertNotEqual(STATE_COLORS[state], (0, 0, 0), state)


if __name__ == "__main__":
    unittest.main()
