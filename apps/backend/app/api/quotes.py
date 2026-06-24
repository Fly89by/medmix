import io
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.quote import Quote
from app.schemas.quote import QuoteCreate, QuoteUpdate, QuoteResponse
from app.services.activity import log_activity
from app.services.pdf import generate_quote_pdf
from app.services.notifications import notify_quote_created

QUOTE_STATUSES = ["DRAFT", "SENT", "ACCEPTED", "REJECTED", "EXPIRED"]

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/api/quotes")
async def list_quotes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    search: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Quote).order_by(Quote.created_at.desc())
    if status:
        query = query.where(Quote.status == status.upper())
    if search:
        query = query.where(Quote.customer_name.ilike(f"%{search}%"))

    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    items = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    return {
        "items": items.scalars().all(),
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/api/quotes/{quote_id}", response_model=QuoteResponse)
async def get_quote(quote_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Quote).where(Quote.id == quote_id))
    quote = result.scalar_one_or_none()
    if not quote:
        raise HTTPException(404, "Quote not found")
    return quote


@router.post("/api/quotes", response_model=QuoteResponse, status_code=201)
async def create_quote(
    req: QuoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = req.quantity * req.unit_price
    count = await db.scalar(select(func.count(Quote.id)))
    quote_number = f"Q-{str(count + 1).zfill(4)}"

    quote = Quote(
        quote_number=quote_number,
        customer_name=req.customer_name,
        customer_phone=req.customer_phone,
        customer_email=req.customer_email,
        product=req.product,
        quantity=req.quantity,
        unit_price=req.unit_price,
        total_price=total,
        city=req.city,
        notes=req.notes,
        status="DRAFT",
        created_by=current_user.id,
    )
    db.add(quote)
    await db.flush()
    await db.refresh(quote)

    await log_activity(
        db, "quote", quote.id, "created",
        description=f"Quote {quote_number} for {quote.customer_name}: {total:,.2f} SAR",
        created_by=current_user.id,
    )
    await db.refresh(quote)

    await notify_quote_created(
        quote_number=quote.quote_number,
        customer_name=quote.customer_name,
        customer_email=quote.customer_email,
        total_price=quote.total_price,
        product=quote.product,
    )
    return quote


@router.put("/api/quotes/{quote_id}", response_model=QuoteResponse)
async def update_quote(
    quote_id: int,
    req: QuoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Quote).where(Quote.id == quote_id))
    quote = result.scalar_one_or_none()
    if not quote:
        raise HTTPException(404, "Quote not found")

    update_data = req.model_dump(exclude_unset=True)
    if "status" in update_data:
        if update_data["status"].upper() not in QUOTE_STATUSES:
            raise HTTPException(400, f"Invalid status: {update_data['status']}")

    for key, val in update_data.items():
        if key == "status":
            setattr(quote, key, val.upper())
        else:
            setattr(quote, key, val)

    if "quantity" in update_data or "unit_price" in update_data:
        quote.total_price = quote.quantity * quote.unit_price

    await db.flush()
    await db.refresh(quote)
    await log_activity(db, "quote", quote.id, "updated", created_by=current_user.id)
    return quote


@router.get("/api/quotes/{quote_id}/pdf")
async def download_quote_pdf(quote_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Quote).where(Quote.id == quote_id))
    quote = result.scalar_one_or_none()
    if not quote:
        raise HTTPException(404, "Quote not found")

    pdf_bytes = generate_quote_pdf(quote)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={quote.quote_number}.pdf"},
    )


@router.delete("/api/quotes/{quote_id}")
async def delete_quote(
    quote_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Quote).where(Quote.id == quote_id))
    quote = result.scalar_one_or_none()
    if not quote:
        raise HTTPException(404, "Quote not found")
    await db.delete(quote)
    await log_activity(db, "quote", quote_id, "deleted", created_by=current_user.id)
    return {"message": "Quote deleted"}
