from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.lead import Lead
from app.models.quote import Quote
from app.models.company import Company
from app.models.contact import Contact
from openai import AsyncOpenAI

router = APIRouter(dependencies=[Depends(get_current_user)])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    suggestions: list[str] = []


SYSTEM_PROMPT = """أنت مساعد ذكي لنظام MED.MIX OS - نظام إدارة علاقات العملاء (CRM) للسوق السعودي.
مهمتك مساعدة المستخدم في إدارة المبيعات والعملاء.
تحدث باللغة العربية الفصحى.
كن مختصراً ومفيداً.
إذا سأل المستخدم عن إحصائيات أو بيانات، اطلب منه استخدام قسم التحليلات في لوحة التحكم."""

FALLBACK_RESPONSES = {
    "مرحبا": "مرحباً بك في MED.MIX OS! كيف我可以 مساعدتك؟",
    "مبيعات": "يمكنك متابعة المبيعات من خلال لوحة التحكم.",
    "تقرير": "يمكنك الاطلاع على التقارير في قسم التحليلات.",
    "مساعدة": "الأقسام المتاحة: لوحة التحكم، إدارة العملاء، العملاء المحتملين، عروض الأسعار، التحليلات، المساعد الذكي.",
}
FALLBACK_DEFAULT = "شكراً لتواصلك. يمكنك استخدام الأقسام المختلفة في النظام لإدارة أعمالك."


async def get_crm_context(db: AsyncSession) -> str:
    companies = await db.scalar(select(func.count(Company.id)))
    contacts = await db.scalar(select(func.count(Contact.id)))
    leads = await db.scalar(select(func.count(Lead.id)))
    active = await db.scalar(select(func.count(Lead.id)).where(Lead.status.notin_(["WON", "LOST"])))
    quotes = await db.scalar(select(func.count(Quote.id)))
    return f"الشركات: {companies or 0} | جهات الاتصال: {contacts or 0} | العملاء المحتملين: {leads or 0} | النشطاء: {active or 0} | عروض الأسعار: {quotes or 0}"


@router.post("/api/assistant/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not req.message.strip():
        raise HTTPException(400, "الرجاء إدخال رسالة")

    if settings.openai_api_key:
        try:
            context = await get_crm_context(db)
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"سياق النظام الحالي:\n{context}\n\nرسالة المستخدم: {req.message}"},
                ],
                max_tokens=300,
                temperature=0.7,
            )
            reply = resp.choices[0].message.content or "عذراً، لم أتمكن من معالجة طلبك."
        except Exception as e:
            reply = f"عذراً، حدث خطأ في الاتصال بالمساعد: {str(e)}"
    else:
        msg = req.message.strip().lower()
        reply = FALLBACK_DEFAULT
        for keyword, response in FALLBACK_RESPONSES.items():
            if keyword in msg:
                reply = response
                break

    suggestions = [
        "عرض المبيعات",
        "تقرير شهري",
        "إضافة عميل جديد",
        "إنشاء عرض سعر",
    ]

    return ChatResponse(reply=reply, suggestions=suggestions)
