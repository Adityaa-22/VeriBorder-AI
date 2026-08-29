import cv2

from face_region import detect_faces


image_path = "data/sample_documents/sample_passport.png"

image = cv2.imread(image_path)

if image is None:
    raise ValueError("Could not read passport image.")

faces = detect_faces(image_path)

print("===== FACE DETECTION =====")
print("Faces detected:", len(faces))

for i, face in enumerate(faces, start=1):

    x, y, w, h = [int(v) for v in face[:4]]

    print(
        f"Face {i}: "
        f"x={x}, y={y}, "
        f"width={w}, height={h}"
    )

    # Add some padding around the detected face
    padding_x = int(w * 0.8)
    padding_y = int(h * 0.8)

    x1 = max(0, x - padding_x)
    y1 = max(0, y - padding_y)

    x2 = min(image.shape[1], x + w + padding_x)
    y2 = min(image.shape[0], y + h + padding_y)

    photo_region = image[y1:y2, x1:x2]

    output_path = (
        f"data/sample_documents/photo_region_{i}.jpg"
    )

    cv2.imwrite(output_path, photo_region)

    print(f"Saved: {output_path}")

print("\nPhoto-region extraction completed.")