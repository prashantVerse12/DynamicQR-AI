from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey
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