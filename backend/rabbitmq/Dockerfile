FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY inbox_queue_setup.py .
CMD ["python", "inbox_queue_setup.py"]