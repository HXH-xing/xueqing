# ===== 阶段 1:构建前端(Vite + Vue)=====
FROM node:20-alpine AS frontend
WORKDIR /app
COPY package.json ./
RUN npm install
COPY index.html vite.config.js ./
COPY src ./src
COPY App.vue ./
# 不复制 .env → VITE_API_BASE 为空 → 前端走相对路径 /api(前后端同源)
RUN npm run build

# ===== 阶段 2:运行后端(FastAPI 同时托管 API 与前端 dist)=====
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY --from=frontend /app/dist ./dist
RUN mkdir -p data
EXPOSE 8000
# 监听平台指定的 PORT(默认 8000)
CMD ["sh", "-c", "uvicorn 4:app --host 0.0.0.0 --port ${PORT:-8000}"]
