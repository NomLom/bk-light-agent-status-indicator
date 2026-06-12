from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

EMOJI_NATIVE_SIZE = 160
WHITE_THRESHOLD = 220

STATE_COLORS: dict[str, tuple[int, int, int]] = {
    "idle": (0, 0, 0),
    "thinking": (0, 0, 0),
    "tool_use": (0, 0, 0),
    "permission": (0, 0, 0),
    "success": (0, 18, 0),
    "failed": (22, 0, 0),
    "cancelled": (16, 8, 0),
}

EMPTY_BG = (5, 5, 5)


def load_png_sprite(path: Path, size: int) -> Image.Image:
    img = Image.open(path).convert("RGBA")
    r, g, b, a = img.split()
    is_white = Image.merge("RGB", (r, g, b)).convert("L").point(
        lambda p: 0 if p >= WHITE_THRESHOLD else 255
    )
    a = Image.composite(a, Image.new("L", img.size, 0), is_white)
    img = Image.merge("RGBA", (r, g, b, a))
    return img.resize((size, size), Image.LANCZOS)


def render_fullscreen_png(path: Path, canvas_size: tuple[int, int]) -> Image.Image:
    img = Image.open(path).convert("RGBA")
    r, g, b, a = img.split()
    is_white = Image.merge("RGB", (r, g, b)).convert("L").point(
        lambda p: 0 if p >= WHITE_THRESHOLD else 255
    )
    a = Image.composite(a, Image.new("L", img.size, 0), is_white)
    img = Image.merge("RGBA", (r, g, b, a))
    img = img.resize(canvas_size, Image.LANCZOS)
    bg = Image.new("RGB", canvas_size, (0, 0, 0))
    bg.paste(img, mask=img.split()[3])
    return bg


def render_emoji_sprite(emoji: str, size: int, font_path: Path) -> Image.Image:
    font = ImageFont.truetype(str(font_path), EMOJI_NATIVE_SIZE)
    canvas = Image.new("RGBA", (EMOJI_NATIVE_SIZE, EMOJI_NATIVE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    bbox = draw.textbbox((0, 0), emoji, font=font, embedded_color=True)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (EMOJI_NATIVE_SIZE - tw) // 2 - bbox[0]
    y = (EMOJI_NATIVE_SIZE - th) // 2 - bbox[1]
    draw.text((x, y), emoji, font=font, embedded_color=True)
    return canvas.resize((size, size), Image.LANCZOS)


def build_quadrant(
    sprite: Image.Image,
    bg_color: tuple[int, int, int],
    quad_size: tuple[int, int],
) -> Image.Image:
    quad = Image.new("RGB", quad_size, bg_color)
    emoji_px = min(quad_size) - 2
    resized = sprite.resize((emoji_px, emoji_px), Image.LANCZOS)
    temp = Image.new("RGB", resized.size, bg_color)
    temp.paste(resized, mask=resized.split()[3])
    px = (quad_size[0] - emoji_px) // 2
    py = (quad_size[1] - emoji_px) // 2
    quad.paste(temp, (px, py))
    return quad


def prerender_quadrants(
    statuses: dict[str, str],
    quad_size: tuple[int, int],
    font_path: Path,
    assets_dir: Path,
) -> dict[str, Image.Image]:
    from .config import is_image_path

    sprite_px = min(quad_size)
    quadrants: dict[str, Image.Image] = {}
    for state, value in statuses.items():
        if is_image_path(value):
            png_path = Path(value) if Path(value).is_absolute() else assets_dir / value
            sprite = load_png_sprite(png_path, sprite_px)
        else:
            sprite = render_emoji_sprite(value, sprite_px, font_path)
        bg = STATE_COLORS.get(state, (0, 0, 0))
        quadrants[state] = build_quadrant(sprite, bg, quad_size)
    return quadrants


class SlotManager:
    POSITIONS = [(0, 0), (1, 0), (0, 1), (1, 1)]
    MAX_SLOTS = 4

    def __init__(self) -> None:
        self.slots: list[str | None] = [None] * self.MAX_SLOTS

    def update(self, active_ids: set[str]) -> bool:
        changed = False
        for i in range(self.MAX_SLOTS):
            if self.slots[i] is not None and self.slots[i] not in active_ids:
                self.slots[i] = None
                changed = True
        for sid in sorted(active_ids):
            if sid in self.slots:
                continue
            try:
                free = self.slots.index(None)
            except ValueError:
                break
            self.slots[free] = sid
            changed = True
        return changed

    def snapshot(self, states: dict[str, str]) -> list[str | None]:
        return [states.get(sid) if sid is not None else None for sid in self.slots]


def compose_frame(
    slot_states: list[str | None],
    quadrants: dict[str, Image.Image],
    empty_quad: Image.Image,
    fullscreen_idle: Image.Image,
    canvas_size: tuple[int, int],
) -> Image.Image:
    if all(s is None for s in slot_states):
        return fullscreen_idle
    canvas = Image.new("RGB", canvas_size, (0, 0, 0))
    quad_w = canvas_size[0] // 2
    quad_h = canvas_size[1] // 2
    for i in range(SlotManager.MAX_SLOTS):
        col, row = SlotManager.POSITIONS[i]
        state = slot_states[i]
        quad = quadrants[state] if state is not None else empty_quad
        canvas.paste(quad, (col * quad_w, row * quad_h))
    return canvas
