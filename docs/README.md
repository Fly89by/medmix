# MED.MIX OS - نظام إدارة المبيعات المتكامل

> نظام متكامل لإدارة العملاء والمبيعات وعروض الأسعار مع تقارير وتحليلات ذكية

## 🚀 نظرة عامة

MED.MIX OS هو نظام إدارة مبيعات متكامل مصمم خصيصاً للسوق السعودي، يساعدك على:
- **إدارة العملاء**: تتبع الشركات، جهات الاتصال، والمشاريع
- **إدارة العملاء المتوقعين**: استيراد العملاء من Google Maps، متابعة فرص البيع
- **عروض الأسعار**: إنشاء وإدارة عروض الأسعار مع طباعة PDF
- **التحليلات**: رسوم بيانية ومؤشرات أداء للمبيعات
- **المساعد الذكي**: مساعد ذكي للإجابة على الاستفسارات
- **المهام**: إدارة مهام فريق العمل

---

## 🏗️ المكونات التقنية

```
MED MIX/
├── apps/
│   ├── frontend/          # Next.js 15 (React 19, TypeScript, Tailwind)
│   └── backend/           # FastAPI (Python 3.12, PostgreSQL, SQLAlchemy)
├── database/              # SQL migrations / seeds
├── infrastructure/        # Docker Compose (postgres, redis, minio, backend)
│   └── docker/
├── docs/                  # التوثيق
└── shared/                # الأنماط المشتركة
```

---

## 📋 طريقة تشغيل المشروع

### المتطلبات الأساسية

| الأداة | الإصدار المطلوب |
|--------|----------------|
| Node.js | 18+ |
| Python | 3.12 |
| Docker | 24+ |
| Docker Compose | 2.20+ |

### 1. تشغيل البنية التحتية (Docker)

```bash
# تشغيل الخدمات المساعدة (PostgreSQL، Redis، MinIO) + الباكند
cd infrastructure/docker
docker compose up -d
```

هذا الأمر يشغل:
- **PostgreSQL** (`localhost:5432`) - قاعدة البيانات
- **Redis** (`localhost:6379`) - التخزين المؤقت
- **MinIO** (`localhost:9000`) - تخزين الملفات
- **Backend API** (`localhost:8000`) - السيرفر الرئيسي

### 2. تشغيل الواجهة الأمامية

```bash
cd apps/frontend
npm install
npm run dev
```

التطبيق يعمل على: **http://localhost:3000**

### 3. بيانات الدخول الافتراضية

- **البريد الإلكتروني**: `admin@medmix.com`
- **كلمة المرور**: `admin123`

### 4. تشغيل الاختبارات

```bash
# اختبارات الباكند
cd apps/backend && python -m pytest tests/ -v

# بناء الواجهة الأمامية (فحص الأخطاء)
cd apps/frontend && npm run build
```

---

## 🌐 نشر المشروع

### الواجهة الأمامية على Vercel

```bash
# 1. تثبيت Vercel CLI
npm install -g vercel

# 2. نشر التطبيق
cd apps/frontend
vercel --prod
```

**متغيرات البيئة المطلوبة في Vercel:**
```
NEXT_PUBLIC_API_URL=<your-backend-url>
```

### الباكند - خيارات النشر

الباكند يحتاج PostgreSQL ويتطلب تشغيله على أحد الخيارات:
| الخيار | المنصة | التكلفة |
|--------|--------|---------|
| سحابة | Railway.app / Render.com | ~$7-15/شهر |
| سحابة | Fly.io | ~$5-10/شهر |
| محلي مع نفق | Local Docker + ngrok | مجاني |
| VPS | أي سيرفر مع Docker | ~$10/شهر |

---

## 🗺️ استيراد العملاء من Google Maps

### 1. الحصول على مفتاح Google Maps API

1. اذهب إلى [ Google Cloud Console](https://console.cloud.google.com)
2. أنشئ مشروع جديد أو اختر مشروع موجود
3. فعّل **Places API** من مكتبة APIs
4. اذهب إلى **Credentials** وأنشئ API Key جديد
5. انسخ المفتاح

### 2. إضافة المفتاح إلى الإعدادات

في ملف `.env` في مجلد `apps/backend`:
```
GOOGLE_MAPS_API_KEY=AIzaSy...
```

أو عبر متغير البيئة في Docker:
```yaml
# في docker-compose.yml
environment:
  - GOOGLE_MAPS_API_KEY=AIzaSy...
```

### 3. طريقة الاستخدام في التطبيق

1. سجل دخول إلى التطبيق
2. اذهب إلى **العملاء المتوقعون**
3. اضغط **بحث Google Maps**
4. أدخل نوع النشاط التجاري (مثال: "مطاعم"، "مقاولات")
5. اختر الموقع (اختياري)
6. ستظهر النتائج - اختر ما تريد واستوردها بنقرة واحدة

> **ملاحظة**: بدون مفتاح Google Maps، يعمل النظام بوضع المحاكاة (simulation) ويعطي نتائج وهمية واقعية للسوق السعودي.

---

## 📥 استيراد CSV

يمكنك استيراد العملاء بكميات كبيرة عبر ملف CSV:

1. اضغط على زر **CSV** في صفحة العملاء المتوقعون
2. اختر ملف CSV بالتنسيق التالي:

```csv
company_name,industry,city,phone,email,website,notes
شركة الأمل للتجارة,Retail,الرياض,0550000000,info@alamal.com,https://alamal.com,عميل محتمل
مؤسسة البناء الحديث,Construction,جدة,0561111111,info@bm.com,https://bm.com,مهتم بالمنتجات
```

3. يمكنك تحميل نموذج CSV جاهز بالضغط على **نموذج**

---

## 📧 إشعارات البريد

عند إنشاء عرض سعر جديد، النظام يرسل إشعار للعميل إذا كان البريد الإلكتروني موجوداً.

لتفعيل الإرسال الفعلي، أضف هذه المتغيرات في `.env`:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
```

> بدون إعدادات SMTP، يعمل النظام بوضع المحاكاة (يسجل الإشعار في السجلات فقط).

---

## 🎯 الميزات الرئيسية

### إدارة العملاء (CRM)
- إدارة الشركات، جهات الاتصال، المشاريع
- بحث متقدم مع تصفية
- إضافة وتعديل وحذف

### العملاء المتوقعون (Leads)
- استيراد من Google Maps
- استيراد CSV
- تسجيل تلقائي للدرجة (Lead Scoring)
- انتقال الحالة (NEW → QUALIFIED → CONTACTED → NEGOTIATING → WON/LOST)

### عروض الأسعار (Quotes)
- إنشاء عروض أسعار احترافية
- طباعة PDF
- إشعارات البريد الإلكتروني

### التحليلات (Analytics)
- رسوم بيانية لعروض الأسعار
- تحليل العملاء حسب الحالة والمصدر
- مؤشرات أداء المبيعات

### المساعد الذكي
- مساعد ذكي للمبيعات باللغة العربية
- إجابات فورية عن الاستفسارات
- يقترح أسئلة متابعة

### المهام
- إدارة مهام الفريق
- تتبع الإنجاز
- تصفية حسب الحالة

---

## 🔧 المتغيرات البيئية

### ملف `.env` الرئيسي (في `apps/backend`)

```bash
# التطبيق
APP_NAME=MED.MIX OS
DEBUG=true
SECRET_KEY=your-secret-key-here

# قاعدة البيانات
DATABASE_URL=postgresql+asyncpg://medmix:medmix_pass@localhost:5432/medmix_db

# JWT (الأمان)
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# تخزين الملفات
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=medmix
MINIO_SECRET_KEY=medmix_secret

# Google Maps (اختياري)
GOOGLE_MAPS_API_KEY=

# البريد الإلكتروني (اختياري)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=

# الواجهة الأمامية
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## 📞 الدعم الفني

للاستفسارات والدعم الفني، يرجى التواصل عبر البريد الإلكتروني أو فتح issue في المستودع.

---

## 📄 الترخيص

MED.MIX OS © 2026. جميع الحقوق محفوظة.
