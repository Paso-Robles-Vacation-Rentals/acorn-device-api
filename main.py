from fastapi import FastAPI, HTTPException, Response
from starlette.middleware.cors import CORSMiddleware

import wifi

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", status_code=418)
async def root():
    return {"message": "Acorn Guide"}

@app.get("/wifi/status")
def status():
    return wifi.status()

@app.get("/wifi/scan")
def scan():
    return wifi.scan()

@app.post("/wifi/connect")
def connect(req: dict):
    ssid = req.get("ssid")
    password = req.get("password")

    if not ssid:
        raise HTTPException(400, "SSID required")

    if not wifi.connect(ssid, password):
        return HTTPException(status_code=502, detail="Connection Failed")
    return Response(status_code=200)
