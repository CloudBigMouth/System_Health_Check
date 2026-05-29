import os
import psutil
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

# Ngưỡng alert từ env
CPU_ALERT  = float(os.getenv("CPU_ALERT",  80))
RAM_ALERT  = float(os.getenv("RAM_ALERT",  80))
DISK_ALERT = float(os.getenv("DISK_ALERT", 85))
SWAP_ALERT = float(os.getenv("SWAP_ALERT", 80))
DISK_PATH  = os.getenv("DISK_PATH", "/")
API_KEY    = os.getenv("API_KEY", "")


def auth(key: str):
    if API_KEY and key != API_KEY:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    return None


def respond(value: float, threshold: float, name: str, extra: dict = {}):
    alert = value > threshold
    data = {
        "status": "alert" if alert else "ok",
        "metric": name,
        "value": round(value, 1),
        "threshold": threshold,
        "alert": f"{name} {value:.1f}% > {threshold}%" if alert else None,
        **extra,
    }
    return JSONResponse(status_code=503 if alert else 200, content=data)


# ── Tổng hợp ────────────────────────────────────────────────
@app.get("/health")
def health(key: str = ""):
    if (err := auth(key)):
        return err

    cpu  = psutil.cpu_percent(interval=1)
    ram  = psutil.virtual_memory()
    disk = psutil.disk_usage(DISK_PATH)
    swap = psutil.swap_memory()

    alerts = []
    if cpu  > CPU_ALERT:  alerts.append(f"CPU {cpu:.1f}% > {CPU_ALERT}%")
    if ram.percent  > RAM_ALERT:  alerts.append(f"RAM {ram.percent:.1f}% > {RAM_ALERT}%")
    if disk.percent > DISK_ALERT: alerts.append(f"Disk {disk.percent:.1f}% > {DISK_ALERT}%")
    if swap.percent > SWAP_ALERT: alerts.append(f"Swap {swap.percent:.1f}% > {SWAP_ALERT}%")

    data = {
        "status": "alert" if alerts else "ok",
        "alerts": alerts,
        "metrics": {
            "cpu_percent":  cpu,
            "ram_percent":  round(ram.percent, 1),
            "disk_percent": round(disk.percent, 1),
            "swap_percent": round(swap.percent, 1),
        },
        "thresholds": {
            "cpu":  CPU_ALERT,
            "ram":  RAM_ALERT,
            "disk": DISK_ALERT,
            "swap": SWAP_ALERT,
        },
    }
    return JSONResponse(status_code=503 if alerts else 200, content=data)


# ── Từng metric riêng ────────────────────────────────────────
@app.get("/cpu")
def cpu(key: str = ""):
    if (err := auth(key)):
        return err
    value = psutil.cpu_percent(interval=1)
    count = psutil.cpu_count()
    return respond(value, CPU_ALERT, "CPU", {"cpu_count": count})


@app.get("/ram")
def ram(key: str = ""):
    if (err := auth(key)):
        return err
    m = psutil.virtual_memory()
    return respond(m.percent, RAM_ALERT, "RAM", {
        "total_gb":     round(m.total / 1024**3, 2),
        "used_gb":      round(m.used  / 1024**3, 2),
        "available_gb": round(m.available / 1024**3, 2),
    })


@app.get("/disk")
def disk(key: str = ""):
    if (err := auth(key)):
        return err
    d = psutil.disk_usage(DISK_PATH)
    return respond(d.percent, DISK_ALERT, "Disk", {
        "path":       DISK_PATH,
        "total_gb":   round(d.total / 1024**3, 2),
        "used_gb":    round(d.used  / 1024**3, 2),
        "free_gb":    round(d.free  / 1024**3, 2),
    })


@app.get("/swap")
def swap(key: str = ""):
    if (err := auth(key)):
        return err
    s = psutil.swap_memory()
    return respond(s.percent, SWAP_ALERT, "Swap", {
        "total_gb": round(s.total / 1024**3, 2),
        "used_gb":  round(s.used  / 1024**3, 2),
        "free_gb":  round(s.free  / 1024**3, 2),
    })


# ── Root ─────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "service": "system-health-check",
        "endpoints": ["/health", "/cpu", "/ram", "/disk", "/swap"],
    }
