FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# docker 本地跑在容器里需注释掉
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]