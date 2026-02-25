from fastapi import FastAPI, HTTPException, Response
from starlette.middleware.cors import CORSMiddleware

import wifi

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

wifi = wifi.Wifi()

@app.get("/", status_code=418)
async def root():
    return {"message": "Acorn Guide"}

@app.get("/wifi/status")
def status():
    return wifi.status()

@app.get("/wifi/networks")
def networks():
    return [{
        "ssid": net.ssid,
        "signal": net.signal,
        "security": net.security,
    } for net in wifi.get_networks()]

@app.post("/wifi/connect")
def connect(req: dict):
    ssid = req.get("ssid")
    password = req.get("password")

    if not ssid:
        raise HTTPException(400, "SSID required")

    success, err = wifi.connect(ssid, password)
    if not success:
        raise HTTPException(status_code=502, detail=err)
    return {"status": "connected"}
