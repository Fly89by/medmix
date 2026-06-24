from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.company import Company
from app.models.contact import Contact
from app.models.project import Project
from app.models.lead import Lead
from app.models.quote import Quote
from app.models.activity import Activity

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/api/dashboard")
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    companies_total = await db.scalar(select(func.count(Company.id)))
    contacts_total = await db.scalar(select(func.count(Contact.id)))
    projects_total = await db.scalar(select(func.count(Project.id)))
    leads_total = await db.scalar(select(func.count(Lead.id)))
    active_leads = await db.scalar(
        select(func.count(Lead.id)).where(Lead.status.notin_(["WON", "LOST"]))
    )
    quotes_this_month = await db.scalar(
        select(func.count(Quote.id)).where(Quote.created_at >= month_start)
    )

    result = await db.execute(
        select(Lead.status, func.count(Lead.id))
        .group_by(Lead.status)
    )
    leads_by_status = {row[0]: row[1] for row in result}

    result = await db.execute(
        select(Activity).order_by(Activity.created_at.desc()).limit(10)
    )
    recent_activities = [
        {
            "id": a.id,
            "action": a.action,
            "entity_type": a.entity_type,
            "description": a.description or f"{a.action} {a.entity_type} #{a.entity_id}",
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in result.scalars()
    ]

    return {
        "companies_total": companies_total or 0,
        "contacts_total": contacts_total or 0,
        "projects_total": projects_total or 0,
        "leads_total": leads_total or 0,
        "active_leads": active_leads or 0,
        "quotes_this_month": quotes_this_month or 0,
        "leads_by_status": leads_by_status,
        "recent_activities": recent_activities,
    }
