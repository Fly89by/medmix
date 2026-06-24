from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.lead import Lead
from app.models.quote import Quote

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/api/analytics/overview")
async def get_analytics(db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)
    months = []
    for i in range(6):
        m = now.month - i
        y = now.year
        while m < 1:
            m += 12
            y -= 1
        months.append((y, m))
    months.reverse()

    quotes_trend = []
    for y, m in months:
        result = await db.execute(
            select(func.count(Quote.id)).where(
                text(f"EXTRACT(YEAR FROM created_at) = {y} AND EXTRACT(MONTH FROM created_at) = {m}")
            )
        )
        quotes_trend.append({"year": y, "month": m, "count": result.scalar() or 0})

    lead_status_result = await db.execute(
        select(Lead.status, func.count(Lead.id)).group_by(Lead.status)
    )
    leads_by_status = {row[0]: row[1] for row in lead_status_result}

    lead_source_result = await db.execute(
        select(Lead.source, func.count(Lead.id)).group_by(Lead.source)
    )
    leads_by_source = {row[0]: row[1] for row in lead_source_result}

    return {
        "quotes_trend": quotes_trend,
        "leads_by_status": leads_by_status,
        "leads_by_source": leads_by_source,
    }
