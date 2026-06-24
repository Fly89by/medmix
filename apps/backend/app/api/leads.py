from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse
from app.services.activity import log_activity
from app.services.scoring import calculate_lead_score

LEAD_STATUSES = ["NEW", "QUALIFIED", "CONTACTED", "NEGOTIATING", "WON", "LOST"]
VALID_TRANSITIONS = {
    "NEW": ["QUALIFIED", "LOST"],
    "QUALIFIED": ["CONTACTED", "LOST"],
    "CONTACTED": ["NEGOTIATING", "QUALIFIED", "LOST"],
    "NEGOTIATING": ["WON", "LOST", "CONTACTED"],
    "WON": [],
    "LOST": ["NEW"],
}

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/api/leads")
async def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    source: str = Query(None),
    search: str = Query(None),
    min_score: int = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Lead).order_by(Lead.created_at.desc())
    if status:
        query = query.where(Lead.status == status.upper())
    if source:
        query = query.where(Lead.source == source)
    if search:
        query = query.where(Lead.company_name.ilike(f"%{search}%"))
    if min_score is not None:
        query = query.where(Lead.score >= min_score)

    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    items = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    return {
        "items": items.scalars().all(),
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/api/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(404, "Lead not found")
    return lead


@router.post("/api/leads", response_model=LeadResponse, status_code=201)
async def create_lead(
    req: LeadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    score = calculate_lead_score(
        industry=req.industry, city=req.city, source=req.source
    )
    lead = Lead(**req.model_dump(), score=score)
    db.add(lead)
    await db.flush()
    await db.refresh(lead)
    await log_activity(
        db, "lead", lead.id, "created",
        description=f"Lead {lead.company_name} created with score {score}",
        created_by=current_user.id,
    )
    return lead


@router.put("/api/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    req: LeadUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(404, "Lead not found")

    update_data = req.model_dump(exclude_unset=True)

    if "status" in update_data:
        new_status = update_data["status"].upper()
        if new_status not in LEAD_STATUSES:
            raise HTTPException(400, f"Invalid status: {new_status}")
        allowed = VALID_TRANSITIONS.get(lead.status, [])
        if new_status not in allowed:
            raise HTTPException(
                400,
                f"Cannot transition from {lead.status} to {new_status}. "
                f"Allowed: {allowed}",
            )

    for key, val in update_data.items():
        setattr(lead, key, val)

    if "industry" in update_data or "city" in update_data:
        lead.score = calculate_lead_score(
            industry=lead.industry, city=lead.city, source=lead.source
        )

    await db.flush()
    await db.refresh(lead)
    await log_activity(
        db, "lead", lead.id, "updated",
        description=f"Lead {lead.company_name} updated",
        created_by=current_user.id,
    )
    return lead


@router.delete("/api/leads/{lead_id}")
async def delete_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(404, "Lead not found")
    await db.delete(lead)
    await log_activity(db, "lead", lead_id, "deleted", created_by=current_user.id)
    return {"message": "Lead deleted"}
