import re


def parse_passport_text(text):
    data = {
        "document_type": "passport",
        "passport_number": None,
        "surname": None,
        "given_names": None,
        "nationality": None,
        "date_of_birth": None,
        "sex": None,
        "place_of_birth": None,
        "date_of_issue": None,
        "date_of_expiry": None,
    }

    # Passport number
    match = re.search(
        r"PASSPORT\s+P\s+IND\s+([A-Z0-9]+)",
        text,
        re.IGNORECASE
    )
    if match:
        data["passport_number"] = match.group(1)

    # Surname
    match = re.search(
        r"Surname\s*\n\s*([A-Z]+)",
        text,
        re.IGNORECASE
    )
    if match:
        data["surname"] = match.group(1)

    # Given names
    match = re.search(
        r"Given Name\(s\)\s*\n\s*([A-Z]+)",
        text,
        re.IGNORECASE
    )
    if match:
        data["given_names"] = match.group(1)

    # Nationality
    match = re.search(
        r"Nationality\s*\n\s*([A-Z]+)",
        text,
        re.IGNORECASE
    )
    if match:
        data["nationality"] = match.group(1)

    # Date of birth
    match = re.search(
        r"Date of Birth\s*\n\s*(\d{2}/\d{2}/\d{4})",
        text,
        re.IGNORECASE
    )
    if match:
        data["date_of_birth"] = match.group(1)

    # Sex
    match = re.search(
        r"Sex\s+([MF])(?:\s|$)",
        text,
        re.IGNORECASE
    )
    if match:
        data["sex"] = match.group(1).upper()

    # Place of birth
    match = re.search(
        r"Place of Birth\s*\n\s*(?:[MF]\s+)?([A-Z][A-Z ,.-]+)",
        text,
        re.IGNORECASE
    )
    if match:
        data["place_of_birth"] = match.group(1).strip()

    # Date of issue
    match = re.search(
        r"Date of Issue.*?\n\s*(\d{2}/\d{2}/\d{4})",
        text,
        re.IGNORECASE | re.DOTALL
    )
    if match:
        data["date_of_issue"] = match.group(1)

    # Date of expiry
    match = re.search(
        r"Date of Expiry.*?(\d{2}/\d{2}/\d{4})",
        text,
        re.IGNORECASE | re.DOTALL
    )
    if match:
        data["date_of_expiry"] = match.group(1)

    return data