FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# 用 --factory 调用 create_app，彻底规避导入期副作用问题
CMD ["python","-c","import os,uvicorn; uvicorn.run('main:create_app', factory=True, host='0.0.0.0', port=int(os.getenv('PORT','8080')), log_level='debug')"]
