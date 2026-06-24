from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func as sqlfunc
from app.core.database import Base, get_db
from app.core.security import get_current_user
from app.models.user import User


class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), default="general")
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=sqlfunc.now())
    updated_at = Column(DateTime(timezone=True), server_default=sqlfunc.now(), onupdate=sqlfunc.now())


class ArticleCreate(BaseModel):
    title: str
    content: str
    category: str = "general"


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None


class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/api/knowledge", response_model=dict)
async def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str = Query(None),
    search: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(KnowledgeArticle).order_by(KnowledgeArticle.created_at.desc())
    if category:
        query = query.where(KnowledgeArticle.category == category)
    if search:
        query = query.where(KnowledgeArticle.title.ilike(f"%{search}%"))
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    rows = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    items = [ArticleResponse.model_validate(r) for r in rows.scalars()]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/api/knowledge/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(KnowledgeArticle).where(KnowledgeArticle.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(404, "Article not found")
    return article


@router.post("/api/knowledge", response_model=ArticleResponse, status_code=201)
async def create_article(
    req: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    article = KnowledgeArticle(title=req.title, content=req.content, category=req.category, created_by=current_user.id)
    db.add(article)
    await db.flush()
    await db.refresh(article)
    return article


@router.put("/api/knowledge/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    req: ArticleUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(KnowledgeArticle).where(KnowledgeArticle.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(404, "Article not found")
    for key, val in req.model_dump(exclude_unset=True).items():
        setattr(article, key, val)
    await db.flush()
    await db.refresh(article)
    return article


@router.delete("/api/knowledge/{article_id}")
async def delete_article(article_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(KnowledgeArticle).where(KnowledgeArticle.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(404, "Article not found")
    await db.delete(article)
    return {"message": "Article deleted"}
