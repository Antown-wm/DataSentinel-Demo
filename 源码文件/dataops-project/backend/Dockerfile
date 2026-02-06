FROM python:3.9-slim
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /app
COPY main.py .
COPY lineage_logic.py .
# 默认启动 API，但在 K8s 里会覆盖这个命令来启动 Worker
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
