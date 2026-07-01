import csv
import io
import json
import random
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user
from app.models.user import User
from app.models.lead import Lead
from app.schemas.lead import LeadResponse
from app.services.activity import log_activity
from app.services.scoring import calculate_lead_score

router = APIRouter(dependencies=[Depends(get_current_user)])

# ---- Simulation data for Saudi businesses ----
SAUDI_CITIES = ["الرياض", "جدة", "مكة", "المدينة", "الدمام", "الخبر", "تبوك", "بريدة", "حائل", "نجران", "جازان", "الطائف", "ينبع"]
SAUDI_INDUSTRIES = ["Construction", "Retail", "Technology", "Healthcare", "Manufacturing", "Real Estate", "Engineering", "Government"]

BUSINESS_NAMES = {
    "مطعم": ["مطعم الأصيل", "مطعم النخبة", "مطعم المذاق", "مطعم السلطان", "مطعم الشرق", "مطعم الفخامة", "مطعم الواحة", "مطعم ليالي الشرق"],
    "مقاول": ["شركة البناء الحديث", "مؤسسة الأساس المتين", "شركة العمران", "مؤسسة البنيان", "شركة الإتقان", "مؤسسة الرواد", "شركة التطوير", "مؤسسة البناء الأخضر"],
    "صيدلية": ["صيدلية الدواء", "صيدلية الشفاء", "صيدلية العافية", "صيدلية الصحة", "صيدلية النهدي", "صيدلية البركة", "صيدلية الحياة", "صيدلية الرعاية"],
    "مكتب": ["مكتب المحامي", "مكتب الاستشارات", "مكتب الهندسة", "مكتب المحاسبة", "مكتب التصميم", "مكتب التسويق", "مكتب العلاقات", "مكتب الإدارة"],
    "مستشفى": ["مستشفى الحياة", "مستشفى الأمل", "مستشفى النور", "مستشفى السلام", "مستشفى الشفاء", "مستشفى الوطن", "مستشفى العيون", "مستشفى الأسنان"],
    "محل": ["محل الملابس", "محل الإلكترونيات", "محل العطور", "محل الهدايا", "محل الأثاث", "محل الساعات", "محل المجوهرات", "محل الأحذية"],
    "شركة": ["شركة التقنية", "شركة الخدمات", "شركة التجارة", "شركة المقاولات", "شركة النقل", "شركة الأمن", "شركة النظافة", "شركة الصيانة"],
}

SAUDI_PHONE_PREFIXES = ["055", "056", "053", "054", "050", "057", "058", "059"]
SAUDI_DOMAINS = ["sa", "com.sa", "net.sa", "org.sa"]


def _generate_simulated_businesses(query: str, location: str, count: int = 10) -> list[dict]:
    results = []
    matched_key = None
    for key in BUSINESS_NAMES:
        if key in query or query in key:
            matched_key = key
            break
    names = BUSINESS_NAMES.get(matched_key, BUSINESS_NAMES["شركة"])

    for i in range(count):
        name = random.choice(names) + " " + str(random.randint(1, 99))
        city = location if location else random.choice(SAUDI_CITIES)
        industry = random.choice(SAUDI_INDUSTRIES)
        phone = f"{random.choice(SAUDI_PHONE_PREFIXES)}{random.randint(1000000, 9999999)}"
        domain = f"{name.replace(' ', '').lower()}.{random.choice(SAUDI_DOMAINS)}"
        results.append({
            "company_name": name.strip(),
            "industry": industry,
            "city": city,
            "phone": phone,
            "email": f"info@{domain}",
            "website": f"https://www.{domain}",
            "source": "google_maps",
            "notes": f"تم استيرادها من بحث Google Maps - {query} في {city}",
        })
    return results


class SearchRequest(BaseModel):
    query: str
    location: Optional[str] = None
    max_results: Optional[int] = 10


OSM_QUERY_TEMPLATE = """
[out:json][timeout:15];
area["name:ar"="{city}"]["admin_level"="8"][boundary="administrative"];
(
  nwr[~"(shop|office|amenity|craft|healthcare)"~"{query}",i](area);
  nwr["name"~"{query}",i](area);
);
out center {limit};
"""


async def _search_openstreetmap(query: str, location: str, limit: int) -> list[dict]:
    import httpx
    city = location or "Riyadh"

    # Try with area-based query first (more precise)
    overpass_query = f"""
    [out:json][timeout:15];
    area["name"~"{city}",i];
    (
      nwr[~"(shop|office|amenity|craft|healthcare)"~"{query}",i](area);
      nwr["name"~"{query}",i](area);
    );
    out center {limit};
    """
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://overpass-api.de/api/interpreter",
                data={"data": overpass_query},
                timeout=20,
            )
            data = resp.json()
    except Exception:
        return []

    results = []
    for element in data.get("elements", []):
        tags = element.get("tags", {})
        name = tags.get("name", tags.get("name:ar", "")).strip()
        if not name:
            continue
        phone = tags.get("phone", "") or tags.get("contact:phone", "")
        email = tags.get("email", "") or tags.get("contact:email", "")
        website = tags.get("website", "") or tags.get("contact:website", "")
        city_tag = tags.get("addr:city", tags.get("city", location or ""))
        street = tags.get("addr:street", "")
        results.append({
            "company_name": name,
            "industry": query,
            "city": city_tag or location or "",
            "phone": phone,
            "email": email,
            "website": website,
            "address": f"{street}, {city_tag}".strip(", "),
            "source": "openstreetmap",
        })
        if len(results) >= limit:
            break
    return results


async def _search_google_maps(query: str, location: str, limit: int) -> list[dict]:
    import httpx
    params = {
        "query": f"{query} {location or ''}",
        "key": settings.google_maps_api_key,
        "language": "ar",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://maps.googleapis.com/maps/api/place/textsearch/json",
            params=params,
            timeout=15,
        )
        data = resp.json()
        if data.get("status") != "OK":
            return []
        results = []
        for place in data.get("results", [])[:limit]:
            results.append({
                "place_id": place.get("place_id"),
                "company_name": place.get("name"),
                "industry": query,
                "city": location or "",
                "phone": "",
                "email": "",
                "website": "",
                "address": place.get("formatted_address", ""),
                "rating": place.get("rating"),
                "source": "google_maps",
            })
        return results


@router.post("/api/leads/import/search")
async def search_businesses(
    req: SearchRequest,
    current_user: User = Depends(get_current_user),
):
    """Search for businesses using OpenStreetMap (free) or Google Maps (if key configured)."""
    if not req.query.strip():
        raise HTTPException(400, "Query is required")

    if settings.google_maps_api_key:
        results = await _search_google_maps(req.query, req.location or "", req.max_results)
        if results:
            return {"results": results, "total": len(results), "mode": "google_maps"}

    results = await _search_openstreetmap(req.query, req.location or "", req.max_results)
    if results:
        return {"results": results, "total": len(results), "mode": "openstreetmap"}

    simulated = _generate_simulated_businesses(req.query, req.location or "", req.max_results)
    return {"results": simulated, "total": len(simulated), "mode": "simulation"}


class BulkImportRequest(BaseModel):
    leads: list[dict]


@router.post("/api/leads/import/bulk")
async def bulk_import_leads(
    req: BulkImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Import multiple leads at once (from search results)."""
    if not req.leads:
        raise HTTPException(400, "No leads provided")

    imported = []
    for item in req.leads:
        company_name = item.get("company_name", "").strip()
        if not company_name:
            continue

        score = calculate_lead_score(
            industry=item.get("industry"),
            city=item.get("city"),
            source="google_maps",
        )
        lead = Lead(
            company_name=company_name,
            industry=item.get("industry"),
            city=item.get("city"),
            phone=item.get("phone"),
            email=item.get("email"),
            website=item.get("website"),
            source="google_maps",
            notes=item.get("notes"),
            score=score,
        )
        db.add(lead)
        await db.flush()
        await db.refresh(lead)
        await log_activity(
            db, "lead", lead.id, "imported",
            description=f"Lead {company_name} imported via Google Maps",
            created_by=current_user.id,
        )
        imported.append(lead)

    return {
        "message": f"تم استيراد {len(imported)} عميل متوقع بنجاح",
        "imported_count": len(imported),
    }


@router.post("/api/leads/import/csv")
async def import_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bulk import leads from a CSV file."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(400, "يجب رفع ملف CSV فقط")

    content = await file.read()
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    rows = list(reader)
    if not rows:
        raise HTTPException(400, "الملف فارغ")

    expected = {"company_name", "industry", "city", "phone", "email", "website", "notes"}
    missing = expected - set(rows[0].keys()) - {"industry", "city", "phone", "email", "website", "notes"}
    if missing:
        raise HTTPException(400, f"الأعمدة المطلوبة مفقودة: {', '.join(missing)}. العمود company_name إلزامي.")

    imported = []
    errors = 0
    for row in rows:
        name = row.get("company_name", "").strip()
        if not name:
            errors += 1
            continue
        score = calculate_lead_score(
            industry=row.get("industry"),
            city=row.get("city"),
            source="csv_import",
        )
        lead = Lead(
            company_name=name,
            industry=row.get("industry"),
            city=row.get("city"),
            phone=row.get("phone"),
            email=row.get("email"),
            website=row.get("website"),
            notes=row.get("notes"),
            source="csv_import",
            score=score,
        )
        db.add(lead)
        await db.flush()
        await db.refresh(lead)
        await log_activity(
            db, "lead", lead.id, "imported",
            description=f"Lead {name} imported via CSV",
            created_by=current_user.id,
        )
        imported.append(lead)

    return {
        "message": f"تم استيراد {len(imported)} عميل متوقع بنجاح{', مع ' + str(errors) + ' أخطاء' if errors else ''}",
        "imported_count": len(imported),
        "errors": errors,
    }
