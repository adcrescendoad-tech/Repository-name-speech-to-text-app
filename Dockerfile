FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN mkdir -p static && mv index.html static/ 2>/dev/null || true
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN ls -la static/
CMD python app.py
