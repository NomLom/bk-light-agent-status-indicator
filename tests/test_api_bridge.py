from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_status.api_bridge import _event_to_state, write_state


class ApiBridgeTests(unittest.TestCase):
    def test_event_mapping(self) -> None:
        self.assertEqual(_event_to_state("message.delta", {}), "thinking")
        self.assertEqual(_event_to_state("tool.started", {}), "tool_use")
        self.assertEqual(_event_to_state("approval.request", {}), "permission")
        self.assertEqual(_event_to_state("run.completed", {}), "success")
        self.assertEqual(_event_to_state("run.failed", {}), "failed")
        self.assertEqual(_event_to_state("run.cancelled", {}), "cancelled")

    def test_write_state_filters_invalid_values(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_state(root, "abc", "tool_use")
            self.assertEqual((root / "abc").read_text(), "tool_use")
            write_state(root, "abc", "not-a-state")
            self.assertEqual((root / "abc").read_text(), "tool_use")


if __name__ == "__main__":
    unittest.main()
