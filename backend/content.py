import json
import re
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from models import ContentVersion, QRCode


URL_CONTENT_TYPE = "URL"
TEXT_CONTENT_TYPE = "TEXT"
FORM_CONTENT_TYPE = "FORM"
ALLOWED_CONTENT_TYPES = {
    URL_CONTENT_TYPE,
    TEXT_CONTENT_TYPE,
    FORM_CONTENT_TYPE,
}
MAX_URL_LENGTH = 2048
MAX_TEXT_LENGTH = 10000
MAX_FORM_LENGTH = 50 * 1024
MAX_FORM_FIELDS = 20
MAX_FORM_TITLE_LENGTH = 200
MAX_FORM_FIELD_NAME_LENGTH = 64
MAX_FORM_LABEL_LENGTH = 200
ALLOWED_FORM_FIELD_TYPES = {"text", "email", "textarea"}


def validate_url(value: str) -> str:
    if not isinstance(value, str) or len(value) > MAX_URL_LENGTH:
        raise ValueError("URL must be at most 2048 characters")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("URL must use http or https")
    if any(char.isspace() or ord(char) < 32 for char in value):
        raise ValueError("URL contains invalid characters")
    return value


def validate_text(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("text must not be empty")
    if len(value) > MAX_TEXT_LENGTH:
        raise ValueError("text must be at most 10000 characters")
    return value


def validate_form(value: str | dict) -> str:
    try:
        form = json.loads(value) if isinstance(value, str) else value
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("FORM content must be valid JSON") from exc

    if not isinstance(form, dict) or len(json.dumps(form, ensure_ascii=False).encode("utf-8")) > MAX_FORM_LENGTH:
        raise ValueError("FORM content must be at most 50 KB")
    title = form.get("title", "")
    fields = form.get("fields")
    if not isinstance(title, str) or len(title) > MAX_FORM_TITLE_LENGTH:
        raise ValueError("FORM title is invalid")
    if not isinstance(fields, list) or not fields or len(fields) > MAX_FORM_FIELDS:
        raise ValueError("FORM must contain 1 to 20 fields")
    for field in fields:
        if not isinstance(field, dict):
            raise ValueError("FORM fields must be objects")
        if (
            not isinstance(field.get("name"), str)
            or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", field["name"])
            or not isinstance(field.get("label"), str)
            or len(field["label"]) > MAX_FORM_LABEL_LENGTH
            or field.get("type") not in ALLOWED_FORM_FIELD_TYPES
            or not isinstance(field.get("required"), bool)
            or not isinstance(field.get("max_length"), int)
            or field["max_length"] < 1
            or field["max_length"] > MAX_TEXT_LENGTH
        ):
            raise ValueError("FORM contains an invalid field")
    submit_label = form.get("submit_label", "Submit")
    if not isinstance(submit_label, str) or len(submit_label) > MAX_FORM_LABEL_LENGTH:
        raise ValueError("FORM submit label is invalid")
    return json.dumps(form, ensure_ascii=False, separators=(",", ":"))


def normalize_content(content_type: str, content: str | dict) -> str:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Unsupported content type")
    if content_type == URL_CONTENT_TYPE:
        return validate_url(str(content))
    if content_type == TEXT_CONTENT_TYPE:
        return validate_text(content)
    return validate_form(content)


def get_published_content(qr: QRCode) -> ContentVersion | None:
    published = [
        version
        for version in qr.content_versions
        if version.is_published and version.content_type in ALLOWED_CONTENT_TYPES
    ]
    return max(published, key=lambda version: version.version) if published else None


def get_current_version(qr: QRCode) -> ContentVersion | None:
    return get_published_content(qr)


def get_current_content(qr: QRCode) -> str:
    published = get_published_content(qr)
    return published.content if published else qr.content


def create_url_content_version(
    db: Session,
    qr: QRCode,
    content: str,
) -> ContentVersion:
    content = normalize_content(URL_CONTENT_TYPE, content)
    versions = qr.content_versions
    next_version = max(
        (version.version for version in versions),
        default=0,
    ) + 1

    for version in versions:
        version.is_published = False

    current = ContentVersion(
        qr=qr,
        content_type=URL_CONTENT_TYPE,
        content=content,
        version=next_version,
        is_published=True,
    )
    db.add(current)
    return current


def create_content_version(
    db: Session,
    qr: QRCode,
    content_type: str,
    content: str | dict,
) -> ContentVersion:
    normalized = normalize_content(content_type, content)
    next_version = max(
        (version.version for version in qr.content_versions),
        default=0,
    ) + 1
    for version in qr.content_versions:
        version.is_published = False
    current = ContentVersion(
        qr=qr,
        content_type=content_type,
        content=normalized,
        version=next_version,
        is_published=True,
    )
    db.add(current)
    return current


def backfill_legacy_url_content(db: Session) -> int:
    created = 0
    qrs = db.query(QRCode).all()

    for qr in qrs:
        if qr.content_versions:
            continue

        create_url_content_version(db, qr, qr.content)
        created += 1

    if created:
        db.commit()

    return created
