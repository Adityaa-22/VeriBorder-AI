from face_region import detect_faces
from region_analysis import analyze_regions


image_path = "data/sample_documents/sample_passport.png"

faces = detect_faces(image_path)

regions = []

for i, face in enumerate(faces, start=1):

    x, y, w, h = [int(v) for v in face[:4]]

    regions.append({
        "name": f"Portrait {i}",
        "x": x,
        "y": y,
        "width": w,
        "height": h
    })


results = analyze_regions(
    image_path,
    regions
)


print("===== PORTRAIT TAMPERING ANALYSIS =====")

for result in results:

    print(f"\n{result['region']}")
    print(f"    ELA score: {result['ela_score']}/100")
    print(f"    Anomaly level: {result['level']}")

print("\nNOTE:")
print(
    "ELA scores indicate image-level anomalies and "
    "do not independently prove tampering."
)