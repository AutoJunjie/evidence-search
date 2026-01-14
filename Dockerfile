FROM node:18-alpine AS frontend-builder
WORKDIR /app
COPY web/package*.json ./web/
RUN cd web && npm ci
COPY web/ ./web/
RUN cd web && npm run build

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY --from=frontend-builder /app/ui ./ui
EXPOSE 8080
CMD ["python", "app.py"]
