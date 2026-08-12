"""Build Kaggle dataset-cover-image.png (2:1, brand-aligned)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r"c:\Projects\medicine-box-detection-yolov8")
OUT_DIR = ROOT / "data" / "kaggle_publish"
LOGO = ROOT / "docs" / "assets" / "yolocilin-logo.png"
REF = Path(
    r"C:\Users\medak\.cursor\projects\c-Projects-medicine-box-detection-yolov8"
    r"\assets\kaggle-cover-ref.png"
)

W, H = 560, 280


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Soft mint base (brand)
    bg = (232, 245, 238)
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    # Optional soft photographic wash from generated ref (low opacity)
    if REF.exists():
        ref = Image.open(REF).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
        img = Image.blend(img, ref, 0.28)
        draw = ImageDraw.Draw(img)

    # Left panel accent card
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([18, 18, 215, H - 18], radius=16, fill=(255, 255, 255, 210))
    img = Image.alpha_composite(img.convert("RGBA"), card).convert("RGB")
    draw = ImageDraw.Draw(img)

    logo = Image.open(LOGO).convert("RGBA")
    logo_size = 150
    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
    logo_x = 18 + (197 - logo_size) // 2
    logo_y = (H - logo_size) // 2 - 4
    img.paste(logo, (logo_x, logo_y), logo)
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 28)
        font_sub = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 14)
        font_meta = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 12)
        font_chip = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 11)
    except OSError:
        font_title = ImageFont.load_default()
        font_sub = font_title
        font_meta = font_title
        font_chip = font_title

    tx = 240
    accent = (46, 125, 90)
    draw.rounded_rectangle([tx, 72, tx + 4, 210], radius=2, fill=accent)

    x = tx + 14
    draw.text((x, 70), "Yolocilin", font=font_title, fill=(28, 70, 50))
    draw.text((x, 105), "Medicine Box Detection Dataset", font=font_sub, fill=(45, 90, 65))
    draw.text((x, 132), "YOLOv8  ·  Single class: medicine-box", font=font_meta, fill=(70, 110, 90))
    draw.text((x, 152), "395 images  ·  Train/Valid/Test  ·  CC BY 4.0", font=font_meta, fill=(70, 110, 90))

    chips = ["object detection", "computer vision", "privacy-cleaned"]
    cx, cy = x, 185
    for chip in chips:
        bbox = draw.textbbox((0, 0), chip, font=font_chip)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad_x, pad_y = 8, 4
        draw.rounded_rectangle(
            [cx, cy, cx + tw + pad_x * 2, cy + th + pad_y * 2],
            radius=8,
            fill=(210, 232, 218),
            outline=(120, 170, 140),
        )
        draw.text((cx + pad_x, cy + pad_y - 1), chip, font=font_chip, fill=(40, 90, 65))
        cx += tw + pad_x * 2 + 6

    out = OUT_DIR / "dataset-cover-image.png"
    img.save(out, "PNG", optimize=True)
    print(f"wrote {out} size={img.size}")


if __name__ == "__main__":
    main()
