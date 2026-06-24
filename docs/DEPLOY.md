# دليل نشر MED.MIX OS

## 🌐 الواجهة على Vercel ✅ (منشورة)

**الرابط:** https://frontend-steel-three-58.vercel.app

### تحديث المتغيرات:
```bash
cd apps/frontend
vercel env add NEXT_PUBLIC_API_URL production --value <URL> --yes
vercel deploy --prod --yes
```

---

## ⚙️ الباكند على Railway (نحتاج حساب)

### الخطوات:

1. **سجل في Railway** https://railway.app

2. **اربط GitHub** مع Railway

3. **ارفع الكود على GitHub:**
```bash
cd C:\Users\PCD\Downloads\MED MIX
git init
git add .
git commit -m "Initial deploy"
gh repo create medmix --public --push
```

4. **في Railway Dashboard:**
   - New Project → Deploy from GitHub repo → اختر medmix
   - Railway يكتشف Dockerfile تلقائياً ويبني الباكند
   - Add → PostgreSQL → راح يعطيك `DATABASE_URL`
   - Add → Redis → راح يعطيك `REDIS_URL`

5. **ضبط المتغيرات في Railway:**
   - `DATABASE_URL` (من PostgreSQL)
   - `REDIS_URL` (من Redis)
   - `JWT_SECRET_KEY` (أي مفتاح عشوائي)
   - `SECRET_KEY` (أي مفتاح عشوائي)
   - `GOOGLE_MAPS_API_KEY` (اختياري)
   - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL` (اختياري)
   - `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY` (للملفات - أو استخدم S3)

6. **بعد النشر** → خذ رابط Railway (https://medmix-backend.up.railway.app)
   وحط `NEXT_PUBLIC_API_URL=https://medmix-backend.up.railway.app/api` في Vercel

---

## 🏠 التشغيل المحلي

### بسرعة:
```bash
#双击 start.bat
start.bat
```

### يدوي:
```bash
# 1. شغل Docker Desktop
# 2. شغل الخدمات
cd infrastructure\docker
docker compose up -d

# 3. افتح المتصفح
# الواجهة: http://localhost:3000
# API: http://localhost:8000/api
# Swagger: http://localhost:8000/docs

# دخول: admin@medmix.com / admin123
```

---

## 🔑 متغيرات البيئة

| المتغير | الوصف | إجباري |
|---------|-------|--------|
| `DATABASE_URL` | رابط PostgreSQL | ✅ |
| `JWT_SECRET_KEY` | مفتاح التوكن | ✅ |
| `SECRET_KEY` | مفتاح التشفير | ✅ |
| `REDIS_URL` | رابط Redis | ✅ |
| `MINIO_ENDPOINT` | رابط التخزين | اختياري |
| `GOOGLE_MAPS_API_KEY` | مفتاح خرائط Google | اختياري |
| `SMTP_HOST` | خادم البريد | اختياري |
| `OPENAI_API_KEY` | مفتاح الذكاء الاصطناعي | اختياري |

---

## 📊 الميزات

- [x] 🏢 CRM (شركات / جهات اتصال / مشاريع)
- [x] 🎯 إدارة العملاء المتوقعين (Leads)
- [x] 📄 عروض الأسعار (Quotes) مع PDF
- [x] 📈 تحليلات ورسوم بيانية
- [x] 🤖 مساعد ذكي
- [x] 📚 قاعدة معرفة
- [x] ✅ مهام
- [x] 🌐 بحث Google Maps
- [x] 📥 استيراد CSV
- [x] 📧 إشعارات البريد الإلكتروني
- [x] ☁️ منشور على Vercel
