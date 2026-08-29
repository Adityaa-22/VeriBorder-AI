import re


def parse_mrz(text):
    """
    Extract passport information from a two-line TD3 MRZ.
    """

    # Find lines that look like MRZ lines
    lines = [
        line.strip().replace(" ", "")
        for line in text.splitlines()
        if "<" in line
    ]

    # We need at least two MRZ lines
    if len(lines) < 2:
        return {
            "valid_mrz_format": False,
            "error": "MRZ lines not found"
        }

    line1 = lines[-2]
    line2 = lines[-1]

    # TD3 passport MRZ normally has 44 characters per line.
    # OCR may add/remove characters, so we don't enforce this strictly yet.
    result = {
        "valid_mrz_format": True,
        "document_type": None,
        "country_code": None,
        "surname": None,
        "given_names": None,
        "passport_number": None,
        "nationality": None,
        "date_of_birth": None,
        "sex": None,
        "date_of_expiry": None
    }

    # -------------------------
    # LINE 1
    # -------------------------

    if line1.startswith("P"):
        result["document_type"] = "P"

    if len(line1) >= 5:
        result["country_code"] = line1[2:5]

    # Name section begins after P<XXX
    if len(line1) > 5:
        name_part = line1[5:]

        name_parts = name_part.split("<<")

        surname = name_parts[0].replace("<", " ").strip()

        given_names = ""
        if len(name_parts) > 1:
            given_names = name_parts[1].replace("<", " ").strip()

        result["surname"] = surname or None
        result["given_names"] = given_names or None

    # -------------------------
    # LINE 2
    # -------------------------

    if len(line2) >= 9:

        # Passport number
        result["passport_number"] = line2[0:9].replace("<", "")

        # Nationality
        if len(line2) >= 13:
            result["nationality"] = line2[10:13]

        # Date of birth
        if len(line2) >= 19:
            dob = line2[13:19]
            result["date_of_birth"] = dob

        # Sex
        if len(line2) >= 21:
            result["sex"] = line2[20]

        # Date of expiry
        if len(line2) >= 27:
            expiry = line2[21:27]
            result["date_of_expiry"] = expiry

    return result