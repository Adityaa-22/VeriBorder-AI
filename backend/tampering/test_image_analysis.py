from image_analysis import analyze_image


image_path = "data/sample_documents/sample_passport.png"

result = analyze_image(image_path)

print("===== IMAGE ANALYSIS =====")

print("Format:", result["format"])
print("Width:", result["width"])
print("Height:", result["height"])
print("Has EXIF:", result["has_exif"])

print("\n===== METADATA =====")

if result["metadata"]:
    for key, value in result["metadata"].items():
        print(f"{key}: {value}")
else:
    print("No EXIF metadata found.")