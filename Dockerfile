FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p static
RUN if [ -f index.html ]; then mv index.html static/; fi
RUN ls -la static/
CMD python app.py
