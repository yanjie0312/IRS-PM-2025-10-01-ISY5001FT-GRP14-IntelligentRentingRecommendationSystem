FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# （可改也可删）改为 8080，更贴近 Cloud Run，EXPOSE 仅文档作用
EXPOSE 8080

# 关键：用 Cloud Run 注入的 PORT（默认 8080）
# CMD ["bash","-lc","uvicorn main:app --host 0.0.0.0 --port ${PORT}"]

CMD ["bash","-lc","uvicorn health_only:app --host 0.0.0.0 --port ${PORT} --log-level debug"]

