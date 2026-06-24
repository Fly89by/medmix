import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.auth import router as auth_router
from app.api.crm import router as crm_router
from app.api.leads import router as leads_router
from app.api.quotes import router as quotes_router
from app.api.dashboard import router as dashboard_router
from app.api.analytics import router as analytics_router
from app.api.assistant import router as assistant_router
from app.api.knowledge import router as knowledge_router
from app.api.tasks import router as tasks_router
from app.api.imports import router as imports_router


async def _create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables in background so server starts immediately for healthcheck
    create_task = asyncio.create_task(_create_tables())
    yield
    create_task.cancel()
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_origin_regex="https://.*\\.vercel\\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(crm_router)
app.include_router(leads_router)
app.include_router(quotes_router)
app.include_router(dashboard_router)
app.include_router(analytics_router)
app.include_router(assistant_router)
app.include_router(knowledge_router)
app.include_router(tasks_router)
app.include_router(imports_router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.app_name}
