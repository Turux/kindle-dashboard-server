FROM python:3.11-slim
WORKDIR /app
RUN pip install flask gunicorn
COPY app.py .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]