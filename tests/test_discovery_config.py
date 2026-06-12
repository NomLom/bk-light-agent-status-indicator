from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_status.config import load_config


class ConfigDiscoveryTests(unittest.TestCase):
    def test_name_prefix_defaults_to_bk(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'config.yaml'
            p.write_text('device:\n  address: ""\n', encoding='utf-8')
            cfg = load_config(p)
            self.assertEqual(cfg.device.name_prefix, 'BK')


if __name__ == '__main__':
    unittest.main()
