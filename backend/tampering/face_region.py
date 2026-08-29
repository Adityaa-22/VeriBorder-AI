import cv2
import os


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "face_detection_yunet_2026may.onnx"
)


def detect_faces(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Could not read image.")

    height, width = image.shape[:2]

    detector = cv2.FaceDetectorYN_create(
        MODEL_PATH,
        "",
        (width, height),
        0.8,
        0.3,
        5000
    )

    detector.setInputSize((width, height))

    _, faces = detector.detect(image)

    if faces is None:
        return []

    return faces