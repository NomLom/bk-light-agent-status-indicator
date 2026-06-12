from __future__ import annotations

import sys
from pathlib import Path

SYSTEM_EMOJI_FONTS: dict[str, list[str]] = {
    "darwin": [
        "/System/Library/Fonts/Apple Color Emoji.ttc",
    ],
    "win32": [
        "C:/Windows/Fonts/seguiemj.ttf",
    ],
    "linux": [
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
        "/usr/share/fonts/noto-color-emoji/NotoColorEmoji.ttf",
        "/usr/share/fonts/google-noto-color-emoji/NotoColorEmoji.ttf",
        "/usr/share/fonts/truetype/noto-color-emoji/NotoColorEmoji.ttf",
    ],
}


def resolve_emoji_font(config_path: str | None = None) -> Path:
    if config_path:
        path = Path(config_path)
        if path.exists():
            return path
        raise RuntimeError(
            f"Emoji font not found at configured path: {config_path}\n"
            "Please verify the path in config.yaml under agent_status.emoji_font"
        )

    platform = sys.platform
    candidates = SYSTEM_EMOJI_FONTS.get(platform, [])
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return path

    tried = "\n  ".join(candidates) if candidates else "(no known paths for this platform)"
    raise RuntimeError(
        f"No emoji font found for platform '{platform}'.\n"
        f"Searched:\n  {tried}\n\n"
        "To fix this, set 'emoji_font' in config.yaml:\n\n"
        "  agent_status:\n"
        "    emoji_font: \"/path/to/your/emoji-font.ttf\"\n\n"
        "Recommended fonts:\n"
        "  - Linux: install 'fonts-noto-color-emoji' (apt) or 'google-noto-color-emoji-fonts' (dnf)\n"
        "  - Or download Noto Color Emoji from https://fonts.google.com/noto/specimen/Noto+Color+Emoji"
    )
