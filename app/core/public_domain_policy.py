from urllib.parse import urlparse


class PublicDomainPolicyError(ValueError):
    pass


APPROVED_PUBLIC_SOURCES = {
    "news.google.com",
    "www.reddit.com",
    "reddit.com",
}

PROHIBITED_DATA_TYPES = {
    "private_messages",
    "emails",
    "phone_numbers",
    "non_public_profiles",
    "login_required_content",
    "payment_data",
    "health_data",
    "precise_location_data",
    "children_data",
    "scraped_personal_identifiers",
}


def assert_public_source(source_url: str) -> None:
    if not source_url:
        raise PublicDomainPolicyError("Public-domain policy violation: source_url is required.")

    host = urlparse(source_url).netloc.lower()
    if host not in APPROVED_PUBLIC_SOURCES:
        raise PublicDomainPolicyError(
            f"Public-domain policy violation: '{host}' is not an approved public source."
        )


def assert_no_prohibited_data(record: dict) -> None:
    declared_type = record.get("data_type")
    if declared_type in PROHIBITED_DATA_TYPES:
        raise PublicDomainPolicyError(
            f"Public-domain policy violation: prohibited data type '{declared_type}'."
        )

    text = str(record.get("raw_text", "")).lower()
    prohibited_markers = [
        "ssn",
        "social security number",
        "credit card",
        "password",
        "private message",
        "dm from",
    ]

    for marker in prohibited_markers:
        if marker in text:
            raise PublicDomainPolicyError(
                f"Public-domain policy violation: detected prohibited marker '{marker}'."
            )


def validate_public_record(record: dict) -> None:
    assert_public_source(record.get("source_url"))
    assert_no_prohibited_data(record)


def validate_public_records(records: list[dict]) -> None:
    for record in records:
        validate_public_record(record)
