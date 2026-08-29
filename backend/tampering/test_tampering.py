from image_analysis import analyze_image, calculate_ela_score


image_path = "data/sample_documents/sample_passport.png"


print("===== TAMPERING ANALYSIS =====")

# Image information
image_data = analyze_image(image_path)

print("\nIMAGE INFORMATION")
print("Format:", image_data["format"])
print("Resolution:", image_data["width"], "x", image_data["height"])

# Metadata
print("\nMETADATA")

if image_data["has_exif"]:
    print("EXIF metadata detected")
else:
    print("No EXIF metadata found")

# ELA
ela_score = calculate_ela_score(image_path)

print("\nELA ANALYSIS")
print("ELA anomaly score:", ela_score, "/ 100")

if ela_score < 30:
    level = "LOW"
elif ela_score < 60:
    level = "MEDIUM"
else:
    level = "HIGH"

print("Anomaly level:", level)

print("\nNOTE:")
print("ELA is an anomaly indicator and does not prove document forgery.")