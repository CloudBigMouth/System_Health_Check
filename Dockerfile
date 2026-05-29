FROM python:3.12-slim

WORKDIR /app

RUN pip install fastapi uvicorn psutil --no-cache-dir

COPY main.py .

# Chạy với quyền host để đọc được disk/cpu thật
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
