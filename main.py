import os
import psutil
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

app = FastAPI()

# Ngưỡng alert từ env, mặc định 80%
CPU_ALERT = float(os.getenv("CPU_ALERT", 80))
RAM_ALERT = float(os.getenv("RAM_ALERT", 80))
DISK_ALERT = float(os.getenv("DISK_ALERT", 85))
DISK_PATH = os.getenv("DISK_PATH", "/")

# API key tùy chọn để bảo vệ endpoint
API_KEY = os.getenv("API_KEY", "")


def check_metrics():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage(DISK_PATH).percent
    return cpu, ram, disk


@app.get("/health")
def health(key: str = ""):
    # Kiểm tra API key nếu được cấu hình
    if API_KEY and key != API_KEY:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    cpu, ram, disk = check_metrics()

    alerts = []
    if cpu > CPU_ALERT:
        alerts.append(f"CPU {cpu:.1f}% > {CPU_ALERT}%")
    if ram > RAM_ALERT:
        alerts.append(f"RAM {ram:.1f}% > {RAM_ALERT}%")
    if disk > DISK_ALERT:
        alerts.append(f"Disk {disk:.1f}% > {DISK_ALERT}%")

    data = {
        "status": "alert" if alerts else "ok",
        "alerts": alerts,
        "metrics": {
            "cpu_percent": cpu,
            "ram_percent": ram,
            "disk_percent": disk,
        },
        "thresholds": {
            "cpu": CPU_ALERT,
            "ram": RAM_ALERT,
            "disk": DISK_ALERT,
        },
    }

    # Uptime Kuma check HTTP status code:
    # 200 = UP, 5xx = DOWN
    if alerts:
        return JSONResponse(status_code=503, content=data)
    return JSONResponse(status_code=200, content=data)


@app.get("/")
def root():
    return {"service": "system-health-check", "endpoint": "/health"}
