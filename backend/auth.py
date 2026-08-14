from passlib.context import CryptContext

from jose import jwt, JWTError

from fastapi import Depends, HTTPException

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from sqlalchemy.orm import Session


from database import SessionLocal

from models import User



# -----------------------
# JWT CONFIG
# -----------------------

SECRET_KEY = "dynamic_qr_ai_secret_key"

ALGORITHM = "HS256"



# -----------------------
# PASSWORD HASHING
# -----------------------

pwd_context = CryptContext(

    schemes=[
        "bcrypt"
    ],

    deprecated="auto"
)



def hash_password(password):

    return pwd_context.hash(
        password
    )




def verify_password(
    plain_password,
    hashed_password
):

    return pwd_context.verify(

        plain_password,

        hashed_password
    )




# -----------------------
# CREATE TOKEN
# -----------------------

def create_token(data: dict):


    token = jwt.encode(

        data,

        SECRET_KEY,

        algorithm=ALGORITHM
    )


    return token





# -----------------------
# CHECK TOKEN
# -----------------------

security = HTTPBearer()



def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()





def get_current_user(

    credentials: HTTPAuthorizationCredentials = Depends(security),

    db: Session = Depends(get_db)

):


    token = credentials.credentials


    try:


        payload = jwt.decode(

            token,

            SECRET_KEY,

            algorithms=[
                ALGORITHM
            ]
        )


        email = payload.get(
            "email"
        )



        if email is None:

            raise HTTPException(

                status_code=401,

                detail="Invalid token"
            )



    except JWTError:


        raise HTTPException(

            status_code=401,

            detail="Token invalid"
        )




    user = (

        db.query(User)

        .filter(
            User.email == email
        )

        .first()

    )



    if user is None:


        raise HTTPException(

            status_code=401,

            detail="User not found"

        )



    return user