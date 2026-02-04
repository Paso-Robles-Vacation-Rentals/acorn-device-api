from fastapi import FastAPI, HTTPException
import wifi

app = FastAPI()

@app.get("/", status_code=418)
async def root():
    return {"message": "Acorn Guide"}

@app.get("/wifi/status")
def status():
    return wifi.status()

@app.get("/api/wifi/scan")
def scan():
    return wifi.scan()

@app.post("/api/wifi/connect")
def connect(req: dict):
    ssid = req.get("ssid")
    password = req.get("password")

    if not ssid:
        raise HTTPException(400, "SSID required")

    return wifi.connect(ssid, password)
