from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.company import Company
from app.models.contact import Contact
from app.models.project import Project
from app.models.activity import Activity
from app.schemas.crm import (
    CompanyCreate, CompanyUpdate, CompanyResponse,
    ContactCreate, ContactUpdate, ContactResponse,
    ProjectCreate, ProjectUpdate, ProjectResponse,
    ActivityResponse,
)
from app.services.activity import log_activity

router = APIRouter(dependencies=[Depends(get_current_user)])


async def paginate(query, db: AsyncSession, page: int, page_size: int):
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    items = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    return {"items": items.scalars().all(), "total": total, "page": page, "page_size": page_size}


# === Companies ===

@router.get("/api/companies")
async def list_companies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Company).order_by(Company.created_at.desc())
    if search:
        query = query.where(Company.name.ilike(f"%{search}%"))
    return await paginate(query, db, page, page_size)


@router.get("/api/companies/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(404, "Company not found")
    return company


@router.post("/api/companies", response_model=CompanyResponse, status_code=201)
async def create_company(
    req: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company = Company(**req.model_dump())
    db.add(company)
    await db.flush()
    await db.refresh(company)
    await log_activity(db, "company", company.id, "created", created_by=current_user.id)
    return company


@router.put("/api/companies/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    req: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(404, "Company not found")
    for key, val in req.model_dump(exclude_unset=True).items():
        setattr(company, key, val)
    await db.flush()
    await db.refresh(company)
    await log_activity(db, "company", company.id, "updated", created_by=current_user.id)
    return company


@router.delete("/api/companies/{company_id}")
async def delete_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(404, "Company not found")
    await db.delete(company)
    await log_activity(db, "company", company_id, "deleted", created_by=current_user.id)
    return {"message": "Company deleted"}


# === Contacts ===

@router.get("/api/contacts")
async def list_contacts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    company_id: int = Query(None),
    search: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Contact, Company.name.label("company_name")).join(Company, Contact.company_id == Company.id).order_by(Contact.created_at.desc())
    if company_id:
        query = query.where(Contact.company_id == company_id)
    if search:
        query = query.where(Contact.name.ilike(f"%{search}%"))
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    rows = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    items = []
    for row in rows:
        contact = row[0]
        contact.company_name = row[1]
        items.append(contact)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/api/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(404, "Contact not found")
    return contact


@router.post("/api/contacts", response_model=ContactResponse, status_code=201)
async def create_contact(
    req: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact = Contact(**req.model_dump())
    db.add(contact)
    await db.flush()
    await db.refresh(contact)
    await log_activity(db, "contact", contact.id, "created", created_by=current_user.id)
    return contact


@router.put("/api/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    req: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(404, "Contact not found")
    for key, val in req.model_dump(exclude_unset=True).items():
        setattr(contact, key, val)
    await db.flush()
    await db.refresh(contact)
    await log_activity(db, "contact", contact.id, "updated", created_by=current_user.id)
    return contact


@router.delete("/api/contacts/{contact_id}")
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(404, "Contact not found")
    await db.delete(contact)
    await log_activity(db, "contact", contact_id, "deleted", created_by=current_user.id)
    return {"message": "Contact deleted"}


# === Projects ===

@router.get("/api/projects")
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    company_id: int = Query(None),
    search: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Project, Company.name.label("company_name")).join(Company, Project.company_id == Company.id).order_by(Project.created_at.desc())
    if company_id:
        query = query.where(Project.company_id == company_id)
    if search:
        query = query.where(Project.project_name.ilike(f"%{search}%"))
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    rows = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    items = []
    for row in rows:
        project = row[0]
        project.company_name = row[1]
        items.append(project)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/api/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")
    return project


@router.post("/api/projects", response_model=ProjectResponse, status_code=201)
async def create_project(
    req: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = Project(**req.model_dump())
    db.add(project)
    await db.flush()
    await db.refresh(project)
    await log_activity(db, "project", project.id, "created", created_by=current_user.id)
    return project


@router.put("/api/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    req: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")
    for key, val in req.model_dump(exclude_unset=True).items():
        setattr(project, key, val)
    await db.flush()
    await db.refresh(project)
    await log_activity(db, "project", project.id, "updated", created_by=current_user.id)
    return project


@router.delete("/api/projects/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")
    await db.delete(project)
    await log_activity(db, "project", project_id, "deleted", created_by=current_user.id)
    return {"message": "Project deleted"}


# === Activities ===

@router.get("/api/activities")
async def list_activities(
    entity_type: str = Query(None),
    entity_id: int = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(Activity).order_by(Activity.created_at.desc())
    if entity_type:
        query = query.where(Activity.entity_type == entity_type)
    if entity_id:
        query = query.where(Activity.entity_id == entity_id)
    return await paginate(query, db, page, page_size)
