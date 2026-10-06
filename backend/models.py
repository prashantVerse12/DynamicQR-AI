from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    func
)

from sqlalchemy.orm import relationship

from database import Base



# -----------------------
# USER TABLE
# -----------------------

class User(Base):

    __tablename__ = "users"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    email = Column(
        String,
        unique=True,
        index=True
    )


    password = Column(
        String
    )



    qr_codes = relationship(
        "QRCode",
        back_populates="owner"
    )






# -----------------------
# QR TABLE + AI SECURITY
# -----------------------

class QRCode(Base):

    __tablename__ = "qr_codes"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    qr_id = Column(
        String,
        unique=True,
        index=True
    )


    content = Column(
        String
    )


    active = Column(
        Boolean,
        default=True
    )


    scans = Column(
        Integer,
        default=0
    )



    # 🤖 AI ENGINE RESULT

    risk_score = Column(
        Integer,
        default=0
    )


    ai_status = Column(
        String,
        default="UNKNOWN"
    )



    # USER RELATION

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )



    owner = relationship(
        "User",
        back_populates="qr_codes"
    )

    content_versions = relationship(
        "ContentVersion",
        back_populates="qr",
        cascade="all, delete-orphan",
        order_by="ContentVersion.version"
    )


class ContentVersion(Base):

    __tablename__ = "content_versions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    qr_code_id = Column(
        Integer,
        ForeignKey("qr_codes.id"),
        nullable=False,
        index=True
    )

    content_type = Column(
        String,
        nullable=False,
        default="URL"
    )

    content = Column(
        String,
        nullable=False
    )

    version = Column(
        Integer,
        nullable=False
    )

    is_published = Column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    qr = relationship(
        "QRCode",
        back_populates="content_versions"
    )