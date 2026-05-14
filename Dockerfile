FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p static && mv index.html static/ 2>/dev/null || true
RUN ls -la static/
CMD python app.py
