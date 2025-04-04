FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY event_registration_queue_setup.py .
CMD ["python", "event_registration_queue_setup.py"]