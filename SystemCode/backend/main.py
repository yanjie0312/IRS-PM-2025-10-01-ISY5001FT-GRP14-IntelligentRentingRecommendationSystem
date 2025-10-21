from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database.config import create_db_and_tables
from app.routes.property import router as property_router
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown

app = FastAPI(
    title="IRRS API",
    description="API for IntelligentRentingREcommendatinoSystem",
    version="0.1.0",
    lifespan=lifespan
)

#---------------------------联调---------------------------
origins = [
    "http://localhost:3000",      # React 开发服务器地址
    "http://127.0.0.1:3000",     # 备用地址
    # "https://your-production-domain.com" # 如果未来有生产环境域名，也加进来
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # 允许访问的源列表
    allow_credentials=True,      # 支持发送 cookies
    allow_methods=["*"],         # 允许所有请求方法 (GET, POST, PUT, etc.)
    allow_headers=["*"],         # 允许所有请求头
)
#---------------------------联调---------------------------

app.include_router(property_router)

@app.get("/")
async def root():
    return {"message": "Welcome to IRRS"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
