from __future__ import annotations

import unittest
from pathlib import Path

from agent_status.display import render_emoji_sprite
from agent_status.emoji_font import resolve_emoji_font


class EmojiFontTests(unittest.TestCase):
    def test_render_emoji_sprite_works_with_system_font(self) -> None:
        font = resolve_emoji_font()
        sprite = render_emoji_sprite("🧠", 16, Path(font))
        self.assertEqual(sprite.size, (16, 16))


if __name__ == "__main__":
    unittest.main()
