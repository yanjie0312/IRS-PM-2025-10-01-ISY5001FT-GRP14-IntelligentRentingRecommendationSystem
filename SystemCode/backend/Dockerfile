FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 关键：把 backend 目录加进 Python 搜索路径
ENV PYTHONPATH="/app/SystemCode/backend:${PYTHONPATH}"

EXPOSE 8080
CMD ["python","-c","import os,uvicorn; uvicorn.run('main:create_app', factory=True, host='0.0.0.0', port=int(os.getenv('PORT','8080')), log_level='debug')"]
