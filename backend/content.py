from sqlalchemy.orm import Session

from models import ContentVersion, QRCode


URL_CONTENT_TYPE = "URL"


def get_published_content(qr: QRCode) -> ContentVersion | None:
    published = [
        version
        for version in qr.content_versions
        if version.is_published and version.content_type == URL_CONTENT_TYPE
    ]
    return max(published, key=lambda version: version.version) if published else None


def get_current_content(qr: QRCode) -> str:
    published = get_published_content(qr)
    return published.content if published else qr.content


def create_url_content_version(
    db: Session,
    qr: QRCode,
    content: str,
) -> ContentVersion:
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
