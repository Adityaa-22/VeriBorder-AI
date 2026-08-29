from ocr import extract_text
from parser import parse_passport_text
from mrz import parse_mrz
from validator import validate_document


image_path = "data/sample_documents/sample_passport.png"

# OCR
text = extract_text(image_path)

print("===== RAW OCR =====")
print(text)

# Visual field extraction
visual_data = parse_passport_text(text)

print("\n===== VISUAL OCR DATA =====")

for key, value in visual_data.items():
    print(f"{key}: {value}")

# MRZ extraction
mrz_data = parse_mrz(text)

print("\n===== MRZ DATA =====")

for key, value in mrz_data.items():
    print(f"{key}: {value}")

# Cross-validation
validation = validate_document(
    visual_data,
    mrz_data
)

print("\n===== CROSS VALIDATION =====")

for field, result in validation.items():
    print(
        f"{field}: {result['status']} "
        f"(Visual: {result['visual']} | "
        f"MRZ: {result['mrz']})"
    )