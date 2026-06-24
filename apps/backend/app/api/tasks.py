from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func as sqlfunc
from app.core.database import Base, get_db
from app.core.security import get_current_user
from app.models.user import User


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    related_type = Column(String(50))
    related_id = Column(Integer)
    assigned_to = Column(Integer)
    status = Column(String(50), default="pending")
    due_date = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=sqlfunc.now())


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    related_type: Optional[str] = None
    related_id: Optional[int] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    related_type: Optional[str] = None
    related_id: Optional[int] = None
    assigned_to: Optional[int] = None
    status: str
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/api/tasks", response_model=dict)
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Task).order_by(Task.created_at.desc())
    if status:
        query = query.where(Task.status == status)
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    rows = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    items = [TaskResponse.model_validate(r) for r in rows.scalars()]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("/api/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    req: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = Task(title=req.title, description=req.description, related_type=req.related_type,
                related_id=req.related_id, assigned_to=req.assigned_to, due_date=req.due_date,
                created_by=current_user.id)
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


@router.put("/api/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    req: TaskUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task not found")
    for key, val in req.model_dump(exclude_unset=True).items():
        setattr(task, key, val)
    if req.status == "completed" and not task.completed_at:
        task.completed_at = datetime.utcnow()
    await db.flush()
    await db.refresh(task)
    return task


@router.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task not found")
    await db.delete(task)
    return {"message": "Task deleted"}
