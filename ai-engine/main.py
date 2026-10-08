from fastapi import FastAPI

from scanner import scan_url


app = FastAPI(

    title="Dynamic QR AI Engine"

)



@app.get("/")
def home():

    return {

        "status":

        "AI Engine Online 🤖"

    }


@app.get("/health")
def health():
    return {"status": "ok"}




@app.post("/scan")
def scan(

    url: str

):

    return scan_url(

        url

    )