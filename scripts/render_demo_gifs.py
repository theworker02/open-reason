"""Render README demo GIFs (terminal walkthroughs)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "demo"
NAVY = (11, 31, 51, 255)
CREAM = (244, 239, 228, 255)
COPPER = (196, 163, 90, 255)
TEAL = (42, 111, 111, 255)
MUTED = (168, 184, 196, 255)
GREEN = (120, 196, 140, 255)


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ("Consolas.ttf", "consola.ttf", "C:/Windows/Fonts/consola.ttf", "DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _draw_terminal(lines: list[tuple[str, tuple[int, int, int, int]]], *, width=900, height=420) -> Image.Image:
    image = Image.new("RGBA", (width, height), NAVY)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((16, 16, width - 16, height - 16), radius=18, outline=COPPER, width=2)
    for index, color in enumerate(((227, 76, 61, 255), (243, 189, 67, 255), (83, 194, 90, 255))):
        draw.ellipse((36 + index * 22, 34, 50 + index * 22, 48), fill=color)
    draw.text((120, 32), "open-reason — terminal", font=_font(16), fill=MUTED)
    y = 72
    body = _font(18)
    for text, color in lines:
        draw.text((40, y), text, font=body, fill=color)
        y += 28
    return image


def _type_frames(prompt: str, command: str, output: list[tuple[str, tuple[int, int, int, int]]]) -> list[Image.Image]:
    frames: list[Image.Image] = []
    prefix = f"$ {command}"
    for index in range(len(prefix) + 1):
        frames.append(_draw_terminal([(prompt, MUTED), (prefix[:index] + ("█" if index < len(prefix) else ""), CREAM)]))
    hold = _draw_terminal([(prompt, MUTED), (prefix, CREAM), *output])
    frames.extend([hold] * 12)
    return frames


def _save_gif(path: Path, frames: list[Image.Image], duration: int = 70) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    converted = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=64) for frame in frames]
    converted[0].save(
        path,
        save_all=True,
        append_images=converted[1:],
        duration=duration,
        loop=0,
        optimize=True,
        disposal=2,
    )


def main() -> None:
    approve = _type_frames(
        "approve sources under the license policy",
        "open-reason sources --approve --apply",
        [
            ("khan_academy_computing   approve_curriculum   verbatim=no", GREEN),
            ("mit_opencourseware       approve_curriculum   verbatim=no", GREEN),
            ("openstax                 approve_curriculum   verbatim=no", GREEN),
            ("reddit                   blocked", (220, 80, 80, 255)),
            ("Wrote sources/registry.yaml", COPPER),
        ],
    )
    build = _type_frames(
        "build the education split from original tasks",
        "open-reason generate --domain education",
        [
            ("Generated 40 examples for education", GREEN),
            ("concept_id and education_level set", TEAL),
            ("quality.verified only after a real check", CREAM),
        ],
    )
    load = _type_frames(
        "load a configuration",
        'python -c "from datasets import load_dataset; load_dataset(\\"theworker02/open-reason\\", \\"coding\\")"',
        [
            ("Dataset(features, num_rows=...)", CREAM),
            ("configs: coding | mathematics | education | core | verified | all", TEAL),
        ],
    )
    _save_gif(OUT / "approve.gif", approve)
    _save_gif(OUT / "generate.gif", build)
    _save_gif(OUT / "load.gif", load)
    print(f"wrote GIFs in {OUT}")


if __name__ == "__main__":
    main()
