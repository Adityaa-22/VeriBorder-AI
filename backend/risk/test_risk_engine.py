from risk_engine import calculate_risk


print("===== TEST 1: OCR/MRZ MISMATCH =====")

validation_results = {
    "passport_number": "MISMATCH",
    "surname": "MATCH",
    "given_names": "MATCH",
    "nationality": "MATCH",
    "date_of_birth": "MATCH",
    "date_of_expiry": "MATCH"
}

tampering_results = [
    {
        "region": "Portrait 1",
        "ela_score": 1.06,
        "level": "LOW"
    },
    {
        "region": "Portrait 2",
        "ela_score": 2.24,
        "level": "LOW"
    }
]

result = calculate_risk(
    validation_results,
    tampering_results,
    metadata_suspicious=False
)

print("Risk Score:", result["risk_score"], "/100")
print("Risk Level:", result["risk_level"])
print("Result:", result["label"])

print("\nReasons:")
for reason in result["reasons"]:
    print("-", reason)


print("\n\n===== TEST 2: MULTIPLE ANOMALIES =====")

validation_results = {
    "passport_number": "MISMATCH",
    "surname": "MATCH",
    "given_names": "MATCH",
    "nationality": "MATCH",
    "date_of_birth": "MATCH",
    "date_of_expiry": "MATCH"
}

tampering_results = [
    {
        "region": "Portrait 1",
        "ela_score": 8.0,
        "level": "MEDIUM"
    },
    {
        "region": "Portrait 2",
        "ela_score": 20.0,
        "level": "HIGH"
    }
]

result = calculate_risk(
    validation_results,
    tampering_results,
    metadata_suspicious=True
)

print("Risk Score:", result["risk_score"], "/100")
print("Risk Level:", result["risk_level"])
print("Result:", result["label"])

print("\nReasons:")
for reason in result["reasons"]:
    print("-", reason)