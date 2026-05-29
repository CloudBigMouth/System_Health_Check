# system-health-check

HTTP endpoint nhỏ để Uptime Kuma monitor CPU/RAM/Disk/Swap của server.

Trả về `200 OK` nếu bình thường, `503 Service Unavailable` nếu vượt ngưỡng.  
Uptime Kuma check HTTP status code → tự báo DOWN khi nhận 503.

---

## Endpoints

| Endpoint | Mô tả |
|----------|-------|
| `GET /health` | Tổng hợp tất cả — dùng cái này là đủ |
| `GET /cpu` | CPU only |
| `GET /ram` | RAM only |
| `GET /disk` | Disk only |
| `GET /swap` | Swap only |

Nếu có `API_KEY`, thêm `?key=xxx` vào mỗi request.

---

## Response

**Bình thường — HTTP 200:**
```json
{
  "status": "ok",
  "alerts": [],
  "metrics": {
    "cpu_percent": 12.5,
    "ram_percent": 45.2,
    "disk_percent": 60.1,
    "swap_percent": 10.0
  },
  "thresholds": {
    "cpu": 80,
    "ram": 80,
    "disk": 85,
    "swap": 80
  }
}
```

**Vượt ngưỡng — HTTP 503:**
```json
{
  "status": "alert",
  "alerts": [
    "CPU 91.2% > 80%",
    "Disk 87.3% > 85%"
  ],
  "metrics": {
    "cpu_percent": 91.2,
    "ram_percent": 55.0,
    "disk_percent": 87.3,
    "swap_percent": 10.0
  }
}
```

**Endpoint riêng lẻ — HTTP 200:**
```json
{
  "status": "ok",
  "metric": "RAM",
  "value": 45.2,
  "threshold": 80,
  "alert": null,
  "total_gb": 8.0,
  "used_gb": 3.6,
  "available_gb": 4.4
}
```

---

## Environment Variables

| Biến | Mặc định | Ý nghĩa |
|------|----------|---------|
| `CPU_ALERT` | `80` | Alert khi CPU > 80% |
| `RAM_ALERT` | `80` | Alert khi RAM > 80% |
| `DISK_ALERT` | `85` | Alert khi Disk > 85% |
| `SWAP_ALERT` | `80` | Alert khi Swap > 80% |
| `DISK_PATH` | `/host` | Mount point cần check |
| `API_KEY` | _(trống)_ | Để trống = không cần auth |

---

## Deploy trên Coolify

**1. Push code lên GitHub**
```bash
git init
git add .
git commit -m "init"
git remote add origin https://github.com/your-username/system-health-check.git
git push -u origin main
```

**2. Tạo resource trên Coolify**
- New Resource → **Docker Compose** → chọn repo

**3. Set environment variables trong Coolify UI**
```
CPU_ALERT=80
RAM_ALERT=80
DISK_ALERT=85
SWAP_ALERT=80
API_KEY=your-secret-key
```

**4. Gắn domain**
- Tab Domains → thêm `health.your-server.com`
- Coolify tự cấp SSL qua Traefik

**5. Deploy**

---

## Cấu hình Uptime Kuma

Tạo monitor cho `/health` (check tất cả cùng lúc):

| Field | Giá trị |
|-------|---------|
| Monitor Type | `HTTP(s)` |
| URL | `https://health.your-server.com/health?key=your-secret-key` |
| Interval | `60` giây |
| Expected Status | `200` |

Hoặc tạo monitor riêng cho từng endpoint để phân biệt alert:

```
https://health.your-server.com/cpu?key=xxx   → monitor "CPU - Server 1"
https://health.your-server.com/ram?key=xxx   → monitor "RAM - Server 1"
https://health.your-server.com/disk?key=xxx  → monitor "Disk - Server 1"
```

---

## Cài nhiều server

Deploy một instance riêng trên mỗi server, đặt domain khác nhau:

```
health.server-1.your-domain.com
health.server-2.your-domain.com
```

Rồi tạo monitor riêng trong Uptime Kuma cho từng server.

---

## Test nhanh

```bash
# Check tổng hợp
curl https://health.your-server.com/health?key=xxx

# Check từng cái
curl https://health.your-server.com/cpu?key=xxx
curl https://health.your-server.com/ram?key=xxx
curl https://health.your-server.com/disk?key=xxx
curl https://health.your-server.com/swap?key=xxx

# Test alert — set ngưỡng thấp tạm thời trong Coolify
# CPU_ALERT=1 → redeploy → gọi /cpu sẽ thấy 503
```

---

## Lưu ý

- `pid: host` trong docker-compose cho phép đọc CPU/RAM thật của host, không phải container
- `/:/host:ro` mount filesystem host để đọc disk usage chính xác
- Nếu CPU luôn thấp bất thường (~0.1%) → `pid: host` chưa hoạt động
- Nếu server chết hoàn toàn → Uptime Kuma không gọi được vào endpoint → tự báo DOWN
