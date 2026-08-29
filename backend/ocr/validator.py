from datetime import datetime


def normalize_name(value):
    if not value:
        return ""

    return value.upper().replace("<", " ").strip()


def normalize_country(value):
    if not value:
        return ""

    value = value.upper().strip()

    # Common OCR confusion in MRZ
    value = value.replace("1", "I")

    return value


def convert_mrz_date(value):
    """
    Convert YYMMDD from MRZ into DD/MM/YYYY.
    """

    if not value or len(value) != 6:
        return None

    try:
        date = datetime.strptime(value, "%y%m%d")
        return date.strftime("%d/%m/%Y")
    except ValueError:
        return None


def compare_field(field, visual_value, mrz_value):
    """
    Compare one field from visual OCR and MRZ.
    """

    if not visual_value or not mrz_value:
        return {
            "status": "UNCERTAIN",
            "visual": visual_value,
            "mrz": mrz_value
        }

    if field in ["surname", "given_names"]:
        visual_value = normalize_name(visual_value)
        mrz_value = normalize_name(mrz_value)

    elif field == "nationality":
        visual_value = normalize_country(visual_value)

        # Visual OCR says full nationality name,
        # while MRZ uses a 3-letter country code.
        country_mapping = {
            "INDIAN": "IND"
        }

        visual_value = country_mapping.get(
            visual_value,
            visual_value
        )

        mrz_value = normalize_country(mrz_value)

    elif field in ["date_of_birth", "date_of_expiry"]:
        if len(mrz_value) == 6:
            mrz_value = convert_mrz_date(mrz_value)

    if visual_value == mrz_value:
        return {
            "status": "MATCH",
            "visual": visual_value,
            "mrz": mrz_value
        }

    return {
        "status": "MISMATCH",
        "visual": visual_value,
        "mrz": mrz_value
    }


def validate_document(visual_data, mrz_data):

    fields = [
        "passport_number",
        "surname",
        "given_names",
        "nationality",
        "date_of_birth",
        "date_of_expiry"
    ]

    results = {}

    for field in fields:
        results[field] = compare_field(
            field,
            visual_data.get(field),
            mrz_data.get(field)
        )

    # Sex is excluded because our visual OCR
    # did not reliably extract it.
    return results