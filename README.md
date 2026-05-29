# System Health Check

HTTP endpoint nhỏ để Uptime Kuma monitor CPU/RAM/Disk.  
Trả về `200 OK` nếu bình thường, `503` nếu vượt ngưỡng.

## Deploy trên Coolify

1. Push code lên GitHub repo
2. Coolify → New Resource → **Docker Compose** → chọn repo
3. Cấu hình env variables trong Coolify UI:

| Biến | Mặc định | Ý nghĩa |
|------|----------|---------|
| `CPU_ALERT` | `80` | Alert khi CPU > 80% |
| `RAM_ALERT` | `80` | Alert khi RAM > 80% |
| `DISK_ALERT` | `85` | Alert khi Disk > 85% |
| `DISK_PATH` | `/host` | Path disk cần check |
| `API_KEY` | _(trống)_ | Bảo vệ endpoint nếu muốn |

## Response

**Bình thường (HTTP 200):**
```json
{
  "status": "ok",
  "alerts": [],
  "metrics": {
    "cpu_percent": 12.5,
    "ram_percent": 45.2,
    "disk_percent": 60.1
  }
}
```

**Vượt ngưỡng (HTTP 503):**
```json
{
  "status": "alert",
  "alerts": ["CPU 91.2% > 80%", "Disk 87.3% > 85%"],
  "metrics": {
    "cpu_percent": 91.2,
    "ram_percent": 55.0,
    "disk_percent": 87.3
  }
}
```

## Cấu hình Uptime Kuma

1. Add New Monitor → Type: **HTTP(s)**
2. URL: `https://your-domain/health`  
   _(nếu có API_KEY: `https://your-domain/health?key=YOUR_KEY`)_
3. Interval: `60` giây
4. **Expected Status Code: `200`**  
   → Uptime Kuma tự báo DOWN khi nhận 503

## Cài nhiều server

Deploy service này lên **mỗi server** cần monitor,  
rồi tạo monitor riêng trong Uptime Kuma cho từng server.
