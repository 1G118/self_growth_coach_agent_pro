from fastapi import FastAPI

from app.db.init_db import init_db
from app.routes import users, logs, goals, agent, dashboard

app = FastAPI(
    title="AI Self Growth Coach Agent Pro",
    version="1.0.0",
    description="一个工程化拆分的 AI 自我成长教练 Agent 后端项目。",
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {
        "name": "AI Self Growth Coach Agent Pro",
        "docs": "http://127.0.0.1:8000/docs",
        "status": "running",
    }


app.include_router(users.router)
app.include_router(logs.router)
app.include_router(goals.router)
app.include_router(agent.router)
app.include_router(dashboard.router)
