from fastapi import (
    FastAPI,
    Depends,
    HTTPException
)

from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session

import uuid
import qrcode
import requests


from database import (
    SessionLocal,
    engine
)

from models import (
    Base,
    QRCode,
    User
)

from content import (
    backfill_legacy_url_content,
    create_url_content_version,
    get_current_content,
)


from schemas import (
    UserCreate,
    UserLogin,
    UpdateQRRequest
)


from auth import (
    hash_password,
    verify_password,
    create_token,
    get_current_user,
    get_optional_current_user
)


# -------------------------
# DATABASE
# -------------------------

Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="Dynamic QR AI Platform",
    description="AI Powered QR Security SaaS"
)



# -------------------------
# CORS
# -------------------------

app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)



# -------------------------
# QR IMAGE SERVER
# -------------------------

app.mount(

    "/qr-images",

    StaticFiles(
        directory="."
    ),

    name="qr-images"

)



# -------------------------
# DB SESSION
# -------------------------

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def migrate_legacy_content():
    db = SessionLocal()
    try:
        backfill_legacy_url_content(db)
    finally:
        db.close()


migrate_legacy_content()






# =========================
# AUTH
# =========================


@app.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    old_user = (
        db.query(User)
        .filter(
            User.email == user.email
        )
        .first()
    )

    if old_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = User(
        email=user.email,
        password=hash_password(user.password)

    )

    db.add(new_user)
    db.commit()

    return {
        "message": "Registered successfully 🚀"
    }


@app.post("/login")
def login(

    user: UserLogin,

    db: Session = Depends(get_db)

):


    db_user = (

        db.query(User)

        .filter(
            User.email == user.email
        )

        .first()

    )


    if not db_user:

        raise HTTPException(
            401,
            "Invalid user"
        )



    if not verify_password(

        user.password,

        db_user.password

    ):

        raise HTTPException(
            401,
            "Wrong password"
        )



    token = create_token(

        {
            "email":

            db_user.email
        }

    )


    return {

        "access_token":

        token,


        "token_type":

        "bearer"

    }






# =========================
# HOME
# =========================


@app.get("/")
def home():

    return {

        "backend":

        "running 🚀",


        "AI":

        "enabled 🤖"

    }







# =========================
# CREATE QR WITH AI
# =========================


@app.post("/create-qr")
def create_qr(

    content_url:str,

    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)

):


    # --------------------
    # AI ENGINE CALL
    # --------------------


    try:


        ai_response = requests.post(

            "http://127.0.0.1:9000/scan",

            params={

                "url":

                content_url

            }

        )


        ai_result = ai_response.json()



    except Exception:


        ai_result = {

            "risk_score":0,

            "status":"AI OFFLINE",

            "reasons":[]

        }



    # BLOCK BAD URL


    if "DANGEROUS" in ai_result["status"]:


        raise HTTPException(

            status_code=400,

            detail={

                "message":

                "Dangerous URL blocked 🚨",


                "ai_report":

                ai_result

            }

        )




    qr_id = str(
        uuid.uuid4()
    )[:8]



    qr_link = (

        f"http://localhost:8000/q/{qr_id}"

    )



    img = qrcode.make(
        qr_link
    )



    img.save(

        f"{qr_id}.png"

    )



    qr = QRCode(

        qr_id=qr_id,

        content=content_url,

        active=True,

        scans=0,

        risk_score=ai_result["risk_score"],

        ai_status=ai_result["status"],

        user_id=current_user.id if current_user else None

    )


    db.add(qr)
    create_url_content_version(
        db,
        qr,
        content_url
    )
    db.commit()



    return {

        "message":

        "QR created with AI scan 🤖",


        "qr_id":

        qr_id,


        "qr_link":

        qr_link,


        "qr_image":

        f"http://localhost:8000/qr-images/{qr_id}.png",


        "AI":

        ai_result

    }


@app.put("/update-qr/{qr_id}")
def update_qr(

    qr_id: str,

    request: UpdateQRRequest,

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)

):

    qr = (
        db.query(QRCode)
        .filter(QRCode.qr_id == qr_id)
        .first()
    )

    if not qr:
        raise HTTPException(
            status_code=404,
            detail="QR not found"
        )

    if qr.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to manage this QR code."
        )

    destination_url = str(request.destination_url)

    try:
        ai_response = requests.post(
            "http://127.0.0.1:9000/scan",
            params={"url": destination_url}
        )

        ai_result = ai_response.json()

    except Exception:
        ai_result = {
            "risk_score": 0,
            "status": "AI OFFLINE",
            "reasons": []
        }

    if "DANGEROUS" in ai_result["status"]:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Dangerous URL blocked 🚨",
                "ai_report": ai_result
            }
        )

    create_url_content_version(
        db,
        qr,
        destination_url
    )
    qr.content = destination_url
    qr.risk_score = ai_result["risk_score"]
    qr.ai_status = ai_result["status"]
    db.commit()

    return {
        "message": "QR destination updated successfully",
        "qr_id": qr.qr_id,
        "destination_url": qr.content,
        "risk_score": qr.risk_score,
        "ai_status": qr.ai_status
    }







# =========================
# SCAN QR
# =========================


@app.get("/q/{qr_id}")
def scan_qr(

    qr_id:str,

    db:Session=Depends(get_db)

):


    qr = (

        db.query(QRCode)

        .filter(
            QRCode.qr_id == qr_id
        )

        .first()

    )


    if not qr:

        return {

            "error":

            "QR not found"

        }



    if qr.active == False:

        return {

            "error":

            "QR disabled"

        }



    qr.scans += 1

    db.commit()



    return RedirectResponse(
        get_current_content(qr)
    )


@app.get("/my-qrs")
def my_qrs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    qrs = (
        db.query(QRCode)
        .filter(QRCode.user_id == current_user.id)
        .all()
    )

    return [
        {
            "qr_id": qr.qr_id,
            "content": get_current_content(qr),
            "scans": qr.scans,
            "active": qr.active,
            "risk_score": qr.risk_score,
            "ai_status": qr.ai_status,
            "qr_link": f"http://localhost:8000/q/{qr.qr_id}",
            "qr_image": f"http://localhost:8000/qr-images/{qr.qr_id}.png"
        }
        for qr in qrs
    ]




# =========================
# DETAILS
# =========================


@app.get("/details/{qr_id}")
def details(

    qr_id:str,

    db:Session=Depends(get_db),
    current_user: User = Depends(get_current_user)

):


    qr = (

        db.query(QRCode)

        .filter(
            QRCode.qr_id == qr_id
        )

        .first()

    )


    if not qr:
        raise HTTPException(
            status_code=404,
            detail="QR not found"
        )

    if qr.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to manage this QR code."
        )



    return {

        "qr_id":

        qr.qr_id,


        "content":

        get_current_content(qr),


        "scans":

        qr.scans,


        "active":

        qr.active,


        "risk_score":

        qr.risk_score,


        "ai_status":

        qr.ai_status,


        "qr_image":

        f"http://localhost:8000/qr-images/{qr.qr_id}.png"

    }
