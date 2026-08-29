from fastapi import FastAPI, UploadFile, File
import tempfile
import os

from backend.ocr.ocr import extract_text
from backend.ocr.parser import parse_passport_text
from backend.ocr.mrz import parse_mrz
from backend.ocr.validator import validate_document

from backend.tampering.image_analysis import analyze_image
from backend.tampering.face_region import detect_faces
from backend.tampering.region_analysis import analyze_regions

from backend.risk.risk_engine import calculate_risk


app = FastAPI(
    title="VeriBorder AI",
    description="AI-based Fake Identity & Document Screening System",
    version="0.3.0"
)


@app.get("/")
def root():
    return {
        "project": "VeriBorder AI",
        "status": "running",
        "problem_statement": "26188"
    }


@app.post("/analyze-document")
async def analyze_document(file: UploadFile = File(...)):

    # --------------------------------
    # SAVE UPLOADED DOCUMENT
    # --------------------------------

    suffix = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_file:

        contents = await file.read()

        temp_file.write(contents)

        temp_path = temp_file.name

    try:

        # ==================================
        # 1. OCR
        # ==================================

        text = extract_text(temp_path)


        # ==================================
        # 2. VISUAL DOCUMENT DATA
        # ==================================

        visual_data = parse_passport_text(text)


        # ==================================
        # 3. MRZ
        # ==================================

        mrz_data = parse_mrz(text)


        # ==================================
        # 4. OCR ↔ MRZ VALIDATION
        # ==================================

        validation = validate_document(
            visual_data,
            mrz_data
        )


        # ==================================
        # 5. IMAGE / METADATA ANALYSIS
        # ==================================

        image_data = analyze_image(temp_path)

        metadata_suspicious = False

        # Currently we only flag metadata when
        # EXIF information exists.
        #
        # Presence of EXIF alone does NOT mean
        # the document is forged.
        #
        # Therefore we keep this False for now.

        metadata_suspicious = False


        # ==================================
        # 6. FACE DETECTION
        # ==================================

        faces = detect_faces(temp_path)

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


        # ==================================
        # 7. REGIONAL TAMPERING ANALYSIS
        # ==================================

        tampering_results = analyze_regions(
            temp_path,
            regions
        )


        # ==================================
        # 8. RISK ENGINE
        # ==================================

        risk = calculate_risk(
            validation,
            tampering_results,
            metadata_suspicious
        )


        # ==================================
        # 9. FINAL RESPONSE
        # ==================================

        return {

            "document_type": visual_data["document_type"],

            "visual_data": visual_data,

            "mrz_data": mrz_data,

            "validation": validation,

            "image_analysis": {
                "format": image_data["format"],
                "width": image_data["width"],
                "height": image_data["height"],
                "has_exif": image_data["has_exif"]
            },

            "face_detection": {
                "faces_detected": len(faces)
            },

            "tampering_analysis": tampering_results,

            "risk_assessment": risk
        }


    finally:

        # Delete temporary uploaded file

        if os.path.exists(temp_path):
            os.remove(temp_path)