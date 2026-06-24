from app.api.auth import router as auth_router
from app.api.crm import router as crm_router
from app.api.leads import router as leads_router
from app.api.quotes import router as quotes_router
from app.api.dashboard import router as dashboard_router
from app.api.analytics import router as analytics_router
from app.api.assistant import router as assistant_router
from app.api.knowledge import router as knowledge_router
from app.api.tasks import router as tasks_router

__all__ = ["auth_router", "crm_router", "leads_router", "quotes_router",
           "dashboard_router", "analytics_router", "assistant_router",
           "knowledge_router", "tasks_router"]
