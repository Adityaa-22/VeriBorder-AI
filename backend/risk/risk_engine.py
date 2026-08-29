def calculate_risk(
    validation_results,
    tampering_results,
    metadata_suspicious=False
):
    """
    Calculate an explainable prototype risk score.

    This is a rule-based screening score.
    It is NOT a probability of fraud.
    """

    score = 0
    reasons = []

    # -----------------------------
    # OCR ↔ MRZ VALIDATION
    # -----------------------------

    for field, result in validation_results.items():

        status = result.get("status")

        if status == "MATCH":
            continue

        elif status == "MISMATCH":
            score += 20
            reasons.append(
                f"{field}: OCR and MRZ mismatch"
            )

        elif status == "UNCERTAIN":
            score += 5
            reasons.append(
                f"{field}: could not be reliably verified"
            )

    # -----------------------------
    # TAMPERING ANALYSIS
    # -----------------------------

    for result in tampering_results:

        level = result["level"]
        region = result["region"]

        if level == "LOW":
            continue

        elif level == "MEDIUM":
            score += 10
            reasons.append(
                f"{region}: medium image anomaly"
            )

        elif level == "HIGH":
            score += 25
            reasons.append(
                f"{region}: high image anomaly"
            )

    # -----------------------------
    # METADATA
    # -----------------------------

    if metadata_suspicious:
        score += 10
        reasons.append(
            "Suspicious document metadata"
        )

    score = min(score, 100)

    # -----------------------------
    # FINAL ASSESSMENT
    # -----------------------------

    if score < 20:
        level = "LOW"
        label = "LOW RISK"

    elif score < 50:
        level = "MEDIUM"
        label = "NEEDS REVIEW"

    else:
        level = "HIGH"
        label = "HIGH RISK"

    return {
        "risk_score": score,
        "risk_level": level,
        "label": label,
        "reasons": reasons
    }