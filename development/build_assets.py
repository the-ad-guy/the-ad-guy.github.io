from pathlib import Path
from shutil import copy2

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE_IMAGE = ROOT / "development" / "source-assets" / "adjusted headshot.jpg"
SOURCE_FAVICON = ROOT / "development" / "source-assets" / "favicon-circle.png"
SOURCE_PDF = ROOT / "development" / "source-assets" / "Tim Gibson Resume.pdf"
IMAGE_OUTPUT = ROOT / "production" / "assets" / "images" / "tim-gibson-headshot.webp"
PDF_OUTPUT = ROOT / "production" / "assets" / "documents" / "Tim Gibson Resume.pdf"
FAVICON_ICO_OUTPUT = ROOT / "production" / "favicon.ico"
FAVICON_IMAGE_DIR = ROOT / "production" / "assets" / "images"
HERO_ASPECT_RATIO = 4 / 5


def build_headshot():
    IMAGE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE_IMAGE) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
        width, height = image.size
        target_width = round(height * HERO_ASPECT_RATIO)
        left = (width - target_width) // 2
        crop = image.crop((left, 0, left + target_width, height))
        crop = crop.resize((480, 600), Image.Resampling.LANCZOS)
        crop.save(IMAGE_OUTPUT, "WEBP", quality=88, method=6)


def copy_resume():
    PDF_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    copy2(SOURCE_PDF, PDF_OUTPUT)


def build_favicons():
    FAVICON_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE_FAVICON) as source:
        icon = source.convert("RGBA")

        apple_icon = icon.resize((180, 180), Image.Resampling.LANCZOS)
        apple_background = Image.new("RGB", apple_icon.size, "#0b2038")
        apple_background.paste(apple_icon, mask=apple_icon.split()[3])
        apple_background.save(FAVICON_IMAGE_DIR / "apple-touch-icon.png")

        icon.resize((32, 32), Image.Resampling.LANCZOS).save(
            FAVICON_IMAGE_DIR / "favicon-32x32.png"
        )
        icon.resize((16, 16), Image.Resampling.LANCZOS).save(
            FAVICON_IMAGE_DIR / "favicon-16x16.png"
        )
        icon.save(FAVICON_ICO_OUTPUT, sizes=[(16, 16), (32, 32), (48, 48)])


if __name__ == "__main__":
    build_headshot()
    copy_resume()
    build_favicons()
