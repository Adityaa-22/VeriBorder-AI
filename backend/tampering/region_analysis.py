from PIL import Image

from backend.tampering.image_analysis import calculate_region_ela_score

def analyze_regions(image_path, regions):
    """
    Analyze detected portrait regions.

    The scores are anomaly indicators only.
    They are not probabilities of forgery.
    """

    image = Image.open(image_path).convert("RGB")

    results = []

    for region in regions:

        name = region["name"]

        x = region["x"]
        y = region["y"]
        width = region["width"]
        height = region["height"]

        crop = image.crop(
            (x, y, x + width, y + height)
        )

        score = calculate_region_ela_score(crop)

        # Prototype thresholds.
        # These are intentionally conservative and should
        # eventually be calibrated using genuine/tampered samples.
        if score < 5:
            level = "LOW"
        elif score < 15:
            level = "MEDIUM"
        else:
            level = "HIGH"

        results.append({
            "region": name,
            "ela_score": score,
            "level": level
        })

    return results