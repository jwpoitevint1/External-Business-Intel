from urllib.parse import urlparse


class PublicDomainPolicyError(ValueError):
    pass


APPROVED_PUBLIC_SOURCES = {
    "news.google.com",
    "msnbc.com",
    "www.msnbc.com",
    "cnn.com",
    "www.cnn.com",
    "bbc.com",
    "www.bbc.com",
    "reuters.com",
    "www.reuters.com",
    "apnews.com",
    "www.apnews.com",
    "nytimes.com",
    "www.nytimes.com",
    "reddit.com",
    "www.reddit.com",
    "x.com",
    "www.x.com",
    "facebook.com",
    "www.facebook.com",
    "instagram.com",
    "www.instagram.com",
    "tiktok.com",
    "www.tiktok.com",
    "snapchat.com",
    "www.snapchat.com",
    "youtube.com",
    "www.youtube.com",
    "web-production-d6ffa.up.railway.app",
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
    "adult_content",
    "pornographic_content",
    "explicit_content",
}

PROHIBITED_MARKERS = [
    "ssn",
    "social security number",
    "credit card",
    "password",
    "private message",
    "dm from",
    "direct message",
    "non-public",
    "login required",
    "adult content",
    "adult site",
    "pornographic",
    "explicit content",
    "explicit adult",
]


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
    for marker in PROHIBITED_MARKERS:
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
