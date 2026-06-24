from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(dependencies=[Depends(get_current_user)])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    suggestions: list[str] = []


LEAD_RESPONSES = {
    "مرحبا": "مرحباً بك في MED.MIX OS! كيف يمكنني مساعدتك؟ يمكنني تقديم معلومات عن العملاء، عروض الأسعار، أو تحليلات المبيعات.",
    "مبيعات": "يمكنك متابعة المبيعات من خلال لوحة التحكم. لديك عملاء محتملين وعروض أسعار نشطة. هل تريد تقريراً تفصيلياً؟",
    "تقرير": "يمكنك الاطلاع على التقارير في قسم التحليلات. يتوفر تحليل شهري لعروض الأسعار والعملاء المتوقعين حسب المصدر والحالة.",
    "مساعدة": "الأقسام المتاحة:\n- لوحة التحكم: نظرة عامة\n- إدارة العملاء: الشركات، جهات الاتصال، المشاريع\n- العملاء المحتملين: إدارة الصفقات\n- عروض الأسعار: إنشاء وإدارة عروض الأسعار\n- التحليلات: رسوم بيانية وتقارير",
}
FALLBACK = "شكراً لتواصلك. يمكنك استخدام الأقسام المختلفة في النظام لإدارة أعمالك. هل هناك شيء محدد تبحث عنه؟"


@router.post("/api/assistant/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, current_user: User = Depends(get_current_user)):
    msg = req.message.strip().lower()
    if not msg:
        raise HTTPException(400, "الرجاء إدخال رسالة")

    reply = FALLBACK
    suggestions = ["عرض المبيعات", "تقرير شهري", "مساعدة", "إحصائيات"]

    for keyword, response in LEAD_RESPONSES.items():
        if keyword in msg:
            reply = response
            break

    return ChatResponse(reply=reply, suggestions=suggestions)
