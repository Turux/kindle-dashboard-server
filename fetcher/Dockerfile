FROM python:3.11-slim
WORKDIR /app
RUN pip install requests feedparser yfinance trafilatura schedule
COPY . .
CMD ["python", "fetch.py"]