from fastapi import (
    FastAPI,
    Depends,
    HTTPException
)

from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

import uuid
import qrcode
import requests
import html
import json
from io import BytesIO


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
    create_content_version,
    get_current_content,
    get_current_version,
    normalize_content,
)


from schemas import (
    UserCreate,
    UserLogin,
    QRContentRequest,
    UpdateQRRequest
)


from auth import (
    hash_password,
    verify_password,
    create_token,
    get_current_user,
    get_optional_current_user
)
from config import AI_ENGINE_URL, CORS_ORIGINS, PUBLIC_BASE_URL
from config import ENVIRONMENT


# -------------------------
# DATABASE
# -------------------------

if ENVIRONMENT == "development":
    Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Dynamic QR AI Platform",
    description="AI Powered QR Security SaaS"
)



# -------------------------
# CORS
# -------------------------

app.add_middleware(

    CORSMiddleware,

    allow_origins=CORS_ORIGINS,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

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


if ENVIRONMENT == "development":
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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/qr-images/{qr_id}.png")
def qr_image(
    qr_id: str,
    db: Session = Depends(get_db),
):
    qr = (
        db.query(QRCode)
        .filter(QRCode.qr_id == qr_id)
        .first()
    )
    if not qr:
        raise HTTPException(status_code=404, detail="QR not found")

    image = qrcode.make(f"{PUBLIC_BASE_URL}/q/{qr.qr_id}")
    image_buffer = BytesIO()
    image.save(image_buffer, format="PNG")
    return Response(content=image_buffer.getvalue(), media_type="image/png")







# =========================
# CREATE QR WITH AI
# =========================


@app.post("/create-qr")
def create_qr(

    content_url: str | None = None,
    request: QRContentRequest | None = None,

    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)

):


    if request is not None:
        content_type = request.content_type
        raw_content = request.content
    else:
        if not content_url:
            raise HTTPException(status_code=422, detail="content_url is required")
        content_type = "URL"
        raw_content = content_url

    try:
        normalized_content = normalize_content(content_type, raw_content)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if content_type == "URL":
        content_url = normalized_content
    else:
        content_url = ""

    # --------------------
    # AI ENGINE CALL
    # --------------------


    if content_type == "URL":
        try:
            ai_response = requests.post(
                f"{AI_ENGINE_URL}/scan",
                params={"url": content_url}
            )
            ai_result = ai_response.json()
        except Exception:
            ai_result = {
                "risk_score": 0,
                "status": "AI OFFLINE",
                "reasons": []
            }
    else:
        ai_result = {
            "risk_score": 0,
            "status": "NOT_APPLICABLE",
            "reasons": []
        }



    # BLOCK BAD URL


    if content_type == "URL" and "DANGEROUS" in ai_result["status"]:


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

        f"{PUBLIC_BASE_URL}/q/{qr_id}"

    )



    qr = QRCode(

        qr_id=qr_id,

        content=normalized_content,

        active=True,

        scans=0,

        risk_score=ai_result["risk_score"],

        ai_status=ai_result["status"],

        user_id=current_user.id if current_user else None

    )


    db.add(qr)
    create_content_version(db, qr, content_type, normalized_content)
    db.commit()



    return {

        "message":

        "QR created with AI scan 🤖",


        "qr_id":

        qr_id,


        "qr_link":

        qr_link,


        "qr_image":

        f"{PUBLIC_BASE_URL}/qr-images/{qr_id}.png",


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

    if request.destination_url is not None:
        content_type = "URL"
        raw_content = str(request.destination_url)
    elif request.content_type is not None and request.content is not None:
        content_type = request.content_type
        raw_content = request.content
    else:
        raise HTTPException(status_code=422, detail="Provide destination_url or content_type and content")

    try:
        normalized_content = normalize_content(content_type, raw_content)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    destination_url = normalized_content

    if content_type == "URL":
        try:
            ai_response = requests.post(
                f"{AI_ENGINE_URL}/scan",
                params={"url": destination_url}
            )
            ai_result = ai_response.json()
        except Exception:
            ai_result = {
                "risk_score": 0,
                "status": "AI OFFLINE",
                "reasons": []
            }
    else:
        ai_result = {
            "risk_score": qr.risk_score,
            "status": qr.ai_status,
            "reasons": []
        }

    if content_type == "URL" and "DANGEROUS" in ai_result["status"]:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Dangerous URL blocked 🚨",
                "ai_report": ai_result
            }
        )

    create_content_version(db, qr, content_type, normalized_content)
    if content_type == "URL":
        qr.content = normalized_content
        qr.risk_score = ai_result["risk_score"]
        qr.ai_status = ai_result["status"]
    db.commit()

    return {
        "message": "QR destination updated successfully",
        "qr_id": qr.qr_id,
        "content_type": content_type,
        "content": normalized_content,
        "destination_url": qr.content if content_type == "URL" else None,
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

    current = next(
        (
            version
            for version in qr.content_versions
            if version.is_published
        ),
        None,
    )
    if current is None:
        try:
            return RedirectResponse(normalize_content("URL", qr.content), status_code=302)
        except ValueError as exc:
            raise HTTPException(status_code=500, detail="Legacy QR content is invalid") from exc

    if current.content_type == "URL":
        return RedirectResponse(current.content, status_code=302)
    if current.content_type == "TEXT":
        return PlainTextResponse(current.content)
    if current.content_type == "FORM":
        form = json.loads(current.content)
        fields = []
        for field in form["fields"]:
            required = " required" if field["required"] else ""
            input_type = "textarea" if field["type"] == "textarea" else "input"
            if input_type == "textarea":
                control = (
                    f'<textarea name="{html.escape(field["name"], quote=True)}"'
                    f' maxlength="{field["max_length"]}"{required}></textarea>'
                )
            else:
                control = (
                    f'<input type="{html.escape(field["type"], quote=True)}"'
                    f' name="{html.escape(field["name"], quote=True)}"'
                    f' maxlength="{field["max_length"]}"{required}>'
                )
            fields.append(
                f'<label>{html.escape(field["label"])}{control}</label>'
            )
        body = (
            "<!doctype html><html><head><meta charset=\"utf-8\">"
            f"<title>{html.escape(form.get('title', 'Form'))}</title></head><body>"
            f"<h1>{html.escape(form.get('title', 'Form'))}</h1>"
            f"<form method=\"post\">{''.join(fields)}"
            f"<button type=\"submit\">{html.escape(form.get('submit_label', 'Submit'))}</button>"
            "</form></body></html>"
        )
        return HTMLResponse(
            body,
            headers={
                "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'"
            },
        )

    raise HTTPException(status_code=500, detail="Unsupported published content type")


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
            "content_type": get_current_version(qr).content_type if get_current_version(qr) else "URL",
            "version": get_current_version(qr).version if get_current_version(qr) else None,
            "scans": qr.scans,
            "active": qr.active,
            "risk_score": qr.risk_score,
            "ai_status": qr.ai_status,
            "qr_link": f"{PUBLIC_BASE_URL}/q/{qr.qr_id}",
            "qr_image": f"{PUBLIC_BASE_URL}/qr-images/{qr.qr_id}.png"
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



    current_version = get_current_version(qr)

    return {

        "qr_id":

        qr.qr_id,


        "content_type": current_version.content_type if current_version else "URL",
        "content": get_current_content(qr),
        "version": current_version.version if current_version else None,


        "scans":

        qr.scans,


        "active":

        qr.active,


        "risk_score":

        qr.risk_score,


        "ai_status":

        qr.ai_status,


        "qr_image":

        f"{PUBLIC_BASE_URL}/qr-images/{qr.qr_id}.png"

    }
