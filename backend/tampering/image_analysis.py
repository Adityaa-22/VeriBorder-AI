from PIL import Image, ImageChops, ImageEnhance
import io


def analyze_image(image_path):
    image = Image.open(image_path)

    result = {
        "format": image.format,
        "width": image.width,
        "height": image.height,
        "has_exif": bool(image.getexif()),
        "metadata": {}
    }

    exif_data = image.getexif()

    for tag_id, value in exif_data.items():
        tag = str(tag_id)

        if isinstance(value, (str, int, float)):
            result["metadata"][tag] = value

    return result


def perform_ela(image_path, quality=90):
    """
    Perform Error Level Analysis.

    ELA is an anomaly indicator, not proof of tampering.
    """

    original = Image.open(image_path).convert("RGB")

    buffer = io.BytesIO()
    original.save(buffer, format="JPEG", quality=quality)

    buffer.seek(0)
    recompressed = Image.open(buffer).convert("RGB")

    difference = ImageChops.difference(
        original,
        recompressed
    )

    enhanced = ImageEnhance.Brightness(
        difference
    ).enhance(10)

    return enhanced


def calculate_ela_score(image_path, quality=90):
    """
    Calculate a basic ELA anomaly score from 0-100.

    Higher values indicate stronger compression differences.
    This is NOT a probability that the document is forged.
    """

    ela_image = perform_ela(image_path, quality)

    pixels = list(ela_image.getdata())

    if not pixels:
        return 0.0

    # Average brightness of ELA image
    total = 0

    for pixel in pixels:
        total += sum(pixel) / 3

    average = total / len(pixels)

    # Convert to a simple 0-100 indicator
    score = min(average / 255 * 100, 100)

    return round(score, 2)


def calculate_region_ela_score(image, quality=90):
    """
    Calculate an ELA score for a PIL image region.
    Returns a 0-100 anomaly indicator.
    """

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="JPEG",
        quality=quality
    )

    buffer.seek(0)

    recompressed = Image.open(buffer).convert("RGB")

    original = image.convert("RGB")

    difference = ImageChops.difference(
        original,
        recompressed
    )

    pixels = list(difference.getdata())

    if not pixels:
        return 0.0

    total = 0

    for pixel in pixels:
        total += sum(pixel) / 3

    average = total / len(pixels)

    score = min((average / 255) * 100, 100)

    return round(score, 2)