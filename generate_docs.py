from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white, navy, silver
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, ListFlowable, ListItem, KeepTogether,
    HRFlowable,
)
from reportlab.platypus.flowables import Flowable
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "MED.MIX_OS_Documentation.pdf")

# Colors
PRIMARY = HexColor("#1e40af")  # primary-700
PRIMARY_LIGHT = HexColor("#3b82f6")  # blue-500
ACCENT = HexColor("#8b5cf6")  # purple-500
BG_LIGHT = HexColor("#f1f5f9")
BG_DARK = HexColor("#1e293b")
TEXT_DARK = HexColor("#0f172a")
TEXT_MUTED = HexColor("#64748b")
BORDER = HexColor("#e2e8f0")

styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    "CoverTitle", fontName="Helvetica-Bold", fontSize=36,
    textColor=white, alignment=TA_CENTER, spaceAfter=12,
))
styles.add(ParagraphStyle(
    "CoverSub", fontName="Helvetica", fontSize=18,
    textColor=HexColor("#93c5fd"), alignment=TA_CENTER, spaceAfter=6,
))
styles.add(ParagraphStyle(
    "CoverInfo", fontName="Helvetica", fontSize=11,
    textColor=HexColor("#cbd5e1"), alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    "SectionTitle", fontName="Helvetica-Bold", fontSize=22,
    textColor=PRIMARY, spaceBefore=24, spaceAfter=12,
    borderPadding=(0, 0, 4, 0),
))
styles.add(ParagraphStyle(
    "SubTitle", fontName="Helvetica-Bold", fontSize=16,
    textColor=TEXT_DARK, spaceBefore=16, spaceAfter=8,
))
styles.add(ParagraphStyle(
    "SubSubTitle", fontName="Helvetica-Bold", fontSize=13,
    textColor=HexColor("#334155"), spaceBefore=12, spaceAfter=6,
))
styles.add(ParagraphStyle(
    "BodyText2", fontName="Helvetica", fontSize=10,
    textColor=TEXT_DARK, leading=16, spaceAfter=6,
    alignment=TA_JUSTIFY,
))
styles.add(ParagraphStyle(
    "CodeBlock", fontName="Courier", fontSize=8,
    textColor=HexColor("#1e293b"), backColor=BG_LIGHT,
    leftIndent=12, rightIndent=12, spaceBefore=4, spaceAfter=8,
    leading=12, borderWidth=1, borderColor=BORDER, borderPadding=6,
))
styles.add(ParagraphStyle(
    "Note", fontName="Helvetica", fontSize=9,
    textColor=HexColor("#d97706"), backColor=HexColor("#fffbeb"),
    leftIndent=12, rightIndent=12, spaceBefore=6, spaceAfter=8,
    leading=14, borderWidth=1, borderColor=HexColor("#fbbf24"), borderPadding=6,
))
styles.add(ParagraphStyle(
    "BulletItem", fontName="Helvetica", fontSize=10,
    textColor=TEXT_DARK, leading=16, spaceAfter=3,
    leftIndent=20, bulletIndent=8,
))
styles.add(ParagraphStyle(
    "TableCell", fontName="Helvetica", fontSize=8,
    textColor=TEXT_DARK, leading=11,
))
styles.add(ParagraphStyle(
    "TableHeader", fontName="Helvetica-Bold", fontSize=9,
    textColor=white, leading=12, alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    "FooterStyle", fontName="Helvetica", fontSize=7,
    textColor=TEXT_MUTED, alignment=TA_CENTER,
))


class ColorBlock(Flowable):
    def __init__(self, width, height, color):
        super().__init__()
        self.width = width
        self.height = height
        self.color = color

    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)


def code(text):
    return Paragraph(text.replace("\n", "<br/>"), styles["CodeBlock"])


def bullet(text):
    return Paragraph(f"<bullet>&bull;</bullet> {text}", styles["BulletItem"])


def note(text):
    return Paragraph(f"<b>Note:</b> {text}", styles["Note"])


def section(title):
    return Paragraph(title, styles["SectionTitle"])


def subtitle(title):
    return Paragraph(title, styles["SubTitle"])


def subsub(title):
    return Paragraph(title, styles["SubSubTitle"])


def body(text):
    return Paragraph(text, styles["BodyText2"])


def make_table(headers, rows):
    data = [headers] + rows
    t = Table(
        data,
        colWidths=None,
        hAlign=TA_LEFT,
    )
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, BG_LIGHT]),
    ]))
    return t


def hr():
    return HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=8, spaceBefore=8)


# Build PDF
doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm,
    topMargin=2*cm, bottomMargin=2*cm,
    title="MED.MIX OS - Documentation",
    author="MED.MIX Team",
)

story = []

# ============== COVER PAGE ==============
story.append(ColorBlock(A4[0], 5.5*cm, PRIMARY))
story.append(Spacer(1, -5.5*cm))
story.append(Spacer(1, 2*cm))
story.append(Paragraph("MED.MIX OS", styles["CoverTitle"]))
story.append(Paragraph("Business Management Operating System", styles["CoverSub"]))
story.append(Spacer(1, 0.5*cm))
story.append(Paragraph("نظام إدارة الأعمال المتكامل", styles["CoverSub"]))
story.append(Spacer(1, 1.5*cm))
story.append(Paragraph("Version 1.0 &mdash; June 2026", styles["CoverInfo"]))
story.append(Paragraph("Saudi Arabia Market &mdash; Arabic-First CRM", styles["CoverInfo"]))
story.append(Spacer(1, 3*cm))
story.append(Paragraph("Deployed on Railway + Vercel", styles["CoverInfo"]))
story.append(Paragraph("Frontend: https://frontend-steel-three-58.vercel.app", styles["CoverInfo"]))
story.append(Paragraph("Backend:  https://backend-production-40db.up.railway.app", styles["CoverInfo"]))
story.append(Spacer(1, 1*cm))
story.append(ColorBlock(A4[0], 0.3*cm, ACCENT))
story.append(PageBreak())

# ============== TABLE OF CONTENTS ==============
story.append(section("Table of Contents"))
story.append(Spacer(1, 0.3*cm))
toc_items = [
    "1. Introduction",
    "2. System Architecture",
    "3. Technology Stack",
    "4. Quick Start & Deployment",
    "5. Authentication & Authorization",
    "6. API Reference",
    "7. Database Schema",
    "8. Real-Time WebSocket System",
    "9. AI Assistant (OpenAI)",
    "10. OpenStreetMap Business Search",
    "11. File Storage",
    "12. Email System",
    "13. User Guide (Arabic)",
    "14. Environment Variables",
    "15. Troubleshooting",
]
for item in toc_items:
    story.append(bullet(item))
story.append(PageBreak())

# ============== 1. INTRODUCTION ==============
story.append(section("1. Introduction"))
story.append(body(
    "MED.MIX OS is a comprehensive business management operating system designed "
    "specifically for the Saudi Arabian market. It provides an all-in-one platform "
    "for managing customers (CRM), sales leads, quotations, tasks, and business "
    "analytics with full Arabic (RTL) support."
))
story.append(body(
    "The system is built as a modern cloud-native application using FastAPI for the "
    "backend and Next.js for the frontend, deployed on Railway and Vercel respectively. "
    "It features real-time multi-user synchronization via WebSockets, an AI-powered "
    "assistant using OpenAI, and business data import from OpenStreetMap."
))

story.append(subtitle("Key Features"))
features = [
    "<b>Arabic-First Interface:</b> Full RTL support with Arabic labels, dates, and number formatting",
    "<b>CRM:</b> Manage companies, contacts, and projects with full CRUD operations",
    "<b>Lead Management:</b> Track sales leads through pipeline stages (New → Qualified → Contacted → Negotiating → Won/Lost)",
    "<b>Quotations:</b> Create and manage price quotes for clients",
    "<b>AI Assistant:</b> Context-aware business assistant powered by OpenAI GPT-4o-mini",
    "<b>Real-Time Sync:</b> WebSocket-based instant updates across all connected users",
    "<b>Business Search:</b> Find and import companies from OpenStreetMap (free, no API key)",
    "<b>Analytics:</b> Visual dashboard with lead distribution, activity feed, and KPIs",
    "<b>Role-Based Access:</b> JWT authentication with role-based permissions",
    "<b>Task Management:</b> Track and assign tasks within the organization",
]
for f in features:
    story.append(bullet(f))
story.append(PageBreak())

# ============== 2. SYSTEM ARCHITECTURE ==============
story.append(section("2. System Architecture"))
story.append(body(
    "MED.MIX OS follows a modern three-tier architecture with clear separation of concerns:"
))

story.append(subtitle("Architecture Overview"))
arch_text = """<b>Frontend (Presentation Layer)</b>
Next.js 14 (App Router) hosted on Vercel
&rarr; RTL Arabic UI with Tailwind CSS
&rarr; Server-side rendering for performance
&rarr; Client components for interactivity

<b>Backend (API Layer)</b>
FastAPI application hosted on Railway
&rarr; RESTful API endpoints
&rarr; WebSocket endpoint for real-time
&rarr; SQLAlchemy async ORM
&rarr; JWT authentication middleware

<b>Database (Data Layer)</b>
PostgreSQL on Railway
&rarr; Relational schema with 10+ tables
&rarr; Async queries via asyncpg driver
&rarr; Redis for caching (optional)

<b>External Services</b>
OpenAI API &rarr; AI Assistant
OpenStreetMap &rarr; Business search
SMTP (optional) &rarr; Email notifications"""
story.append(code(arch_text))

story.append(subtitle("Data Flow"))
story.append(body(
    "1. User interacts with the Next.js frontend (Arabic RTL UI)<br/>"
    "2. Frontend sends API requests to FastAPI backend (with JWT token)<br/>"
    "3. Backend validates auth, processes request, queries PostgreSQL<br/>"
    "4. Response returned as JSON to frontend<br/>"
    "5. On data change, backend broadcasts via WebSocket to all connected clients<br/>"
    "6. All clients automatically refresh their UI"
))
story.append(PageBreak())

# ============== 3. TECHNOLOGY STACK ==============
story.append(section("3. Technology Stack"))

stack_data = [
    ["Layer", "Technology", "Version", "Purpose"],
    ["Frontend", "Next.js", "14.x", "React framework with App Router"],
    [" ", "Tailwind CSS", "3.x", "Utility-first styling"],
    [" ", "TypeScript", "5.x", "Type-safe JavaScript"],
    [" ", "Lucide Icons", "latest", "Icon library"],
    ["Backend", "Python", "3.12", "Runtime"],
    [" ", "FastAPI", "0.115.x", "Async web framework"],
    [" ", "SQLAlchemy", "2.0.x", "Async ORM"],
    [" ", "Pydantic", "2.x", "Data validation"],
    [" ", "python-jose", "latest", "JWT tokens"],
    [" ", "passlib", "latest", "Password hashing"],
    [" ", "OpenAI SDK", "1.50.x", "AI assistant"],
    [" ", "httpx", "latest", "Async HTTP client"],
    ["Database", "PostgreSQL", "16.x", "Primary database"],
    [" ", "asyncpg", "0.30.x", "Async PG driver"],
    ["Infra", "Railway", "-", "Backend hosting"],
    [" ", "Vercel", "-", "Frontend hosting"],
    [" ", "GitHub", "-", "Source control"],
    ["AI", "OpenAI GPT-4o-mini", "-", "AI assistant model"],
    ["Maps", "OpenStreetMap Overpass", "-", "Business data API"],
]
story.append(make_table(stack_data[0], stack_data[1:]))
story.append(PageBreak())

# ============== 4. QUICK START & DEPLOYMENT ==============
story.append(section("4. Quick Start & Deployment"))

story.append(subtitle("Local Development"))
story.append(code(
    "# 1. Clone the repository<br/>"
    "git clone https://github.com/Fly89by/medmix.git<br/>"
    "cd medmix<br/>"
    "<br/>"
    "# 2. Backend setup<br/>"
    "cd apps/backend<br/>"
    "python -m venv .venv<br/>"
    ".venv\\Scripts\\activate  # Windows<br/>"
    "pip install -r requirements.txt<br/>"
    "<br/>"
    "# 3. Configuration<br/>"
    "copy .env.example .env  # Edit with your settings<br/>"
    "<br/>"
    "# 4. Run with Docker (recommended)<br/>"
    "cd infrastructure/docker<br/>"
    "docker compose -p medmix up -d<br/>"
    "<br/>"
    "# 5. Frontend setup<br/>"
    "cd apps/frontend<br/>"
    "npm install<br/>"
    "npm run dev"
))

story.append(subtitle("Deploy to Railway + Vercel"))
steps = [
    "<b>Railway (Backend):</b> Connect GitHub repo &rarr; Set root as project &rarr; Add PostgreSQL &rarr; Set environment variables &rarr; Deploy &rarr; Set domain target port to 8000",
    "<b>Vercel (Frontend):</b> Import GitHub repo &rarr; Set Root Directory to <font face='Courier' size='8'>apps/frontend</font> &rarr; Add <font face='Courier' size='8'>NEXT_PUBLIC_API_URL</font> env var &rarr; Deploy",
    "<b>Post-Deploy:</b> Create admin user via <font face='Courier' size='8'>seed_admin.py</font> script or registration API",
]
for i, s in enumerate(steps):
    story.append(bullet(s))

story.append(subtitle("Seed Admin User"))
story.append(code(
    "# Run from apps/backend/<br/>"
    "python seed_admin.py<br/>"
    "# Creates admin@medmix.com / admin123"
))
story.append(PageBreak())

# ============== 5. AUTHENTICATION ==============
story.append(section("5. Authentication & Authorization"))

story.append(subtitle("Authentication Flow"))
story.append(body(
    "MED.MIX OS uses JWT (JSON Web Tokens) for stateless authentication. "
    "Tokens are issued at login and must be included in the Authorization header "
    "for all protected endpoints."
))

story.append(subtitle("Endpoints"))
auth_data = [
    ["Endpoint", "Method", "Description"],
    ["/api/auth/register", "POST", "Create new user account"],
    ["/api/auth/login", "POST", "Login, returns JWT token"],
    ["/api/auth/me", "GET", "Get current user profile"],
]
story.append(make_table(auth_data[0], auth_data[1:]))

story.append(subtitle("Token Usage"))
story.append(code(
    "# Include in all API requests<br/>"
    "Authorization: Bearer &lt;your-jwt-token&gt;"
))

story.append(subtitle("Roles"))
roles_data = [
    ["Role", "Permissions"],
    ["admin", "Full access to all features and settings"],
    ["manager", "CRUD on companies, contacts, leads, quotes; view analytics"],
    ["user", "Basic CRUD on assigned records; view own tasks"],
]
story.append(make_table(roles_data[0], roles_data[1:]))
story.append(PageBreak())

# ============== 6. API REFERENCE ==============
story.append(section("6. API Reference"))
story.append(body(
    "Base URL: <font face='Courier' size='9'>https://backend-production-40db.up.railway.app/api</font><br/>"
    "All endpoints require JWT authentication unless marked as public."
))

story.append(subtitle("Dashboard"))
api_data = [
    ["GET /api/dashboard", "Get KPIs, lead distribution, recent activity"],
]
story.append(make_table(["Endpoint", "Description"], api_data))

story.append(subtitle("CRM (Companies, Contacts, Projects)"))
api_data = [
    ["GET /api/companies", "List companies (paginated)"],
    ["POST /api/companies", "Create company"],
    ["GET /api/companies/{id}", "Get company details"],
    ["PUT /api/companies/{id}", "Update company"],
    ["DELETE /api/companies/{id}", "Delete company"],
    ["GET /api/contacts", "List contacts"],
    ["POST /api/contacts", "Create contact"],
    ["GET /api/projects", "List projects"],
    ["POST /api/projects", "Create project"],
]
story.append(make_table(["Endpoint", "Description"], api_data))

story.append(subtitle("Leads"))
api_data = [
    ["GET /api/leads", "List leads (paginated, filterable)"],
    ["POST /api/leads", "Create lead"],
    ["GET /api/leads/{id}", "Get lead details"],
    ["PUT /api/leads/{id}", "Update lead"],
    ["DELETE /api/leads/{id}", "Delete lead"],
    ["POST /api/leads/import/search", "Search & import from OpenStreetMap"],
]
story.append(make_table(["Endpoint", "Description"], api_data))

story.append(subtitle("Quotes"))
api_data = [
    ["GET /api/quotes", "List quotations"],
    ["POST /api/quotes", "Create quotation"],
    ["GET /api/quotes/{id}", "Get quote details"],
    ["PUT /api/quotes/{id}", "Update quote"],
    ["DELETE /api/quotes/{id}", "Delete quote"],
]
story.append(make_table(["Endpoint", "Description"], api_data))

story.append(subtitle("AI Assistant"))
api_data = [
    ["POST /api/assistant/chat", "Send message to AI assistant"],
    ["GET /api/assistant/context", "Get CRM context for AI"],
]
story.append(make_table(["Endpoint", "Description"], api_data))

story.append(subtitle("Knowledge Base"))
api_data = [
    ["GET /api/knowledge", "List knowledge entries"],
    ["POST /api/knowledge", "Create entry"],
    ["PUT /api/knowledge/{id}", "Update entry"],
    ["DELETE /api/knowledge/{id}", "Delete entry"],
]
story.append(make_table(["Endpoint", "Description"], api_data))

story.append(subtitle("Tasks"))
api_data = [
    ["GET /api/tasks", "List tasks"],
    ["POST /api/tasks", "Create task"],
    ["PUT /api/tasks/{id}", "Update task"],
    ["DELETE /api/tasks/{id}", "Delete task"],
]
story.append(make_table(["Endpoint", "Description"], api_data))

story.append(subtitle("Real-Time"))
api_data = [
    ["WS /api/ws", "WebSocket - receives real-time data change events"],
]
story.append(make_table(["Endpoint", "Description"], api_data))
story.append(PageBreak())

# ============== 7. DATABASE SCHEMA ==============
story.append(section("7. Database Schema"))
story.append(body(
    "The database uses 10+ tables with foreign key relationships. "
    "All tables use auto-increment integer primary keys and track creation/update timestamps."
))

story.append(subtitle("Tables"))
schema_data = [
    ["Table", "Description", "Key Fields"],
    ["users", "User accounts & auth", "email, password_hash, role, name"],
    ["companies", "Business entities (CRM)", "name, phone, email, address, industry, size"],
    ["contacts", "Contact persons", "name, phone, email, position, company_id (FK)"],
    ["projects", "Tracked projects", "name, status, budget, company_id (FK)"],
    ["leads", "Sales leads pipeline", "name, status (NEW/QUALIFIED/CONTACTED/NEGOTIATING/WON/LOST), source, company_id (FK)"],
    ["quotes", "Price quotations", "quote_number, total, status, lead_id (FK), company_id (FK)"],
    ["activities", "Audit log", "entity_type, entity_id, action, description, created_by (FK users)"],
    ["knowledge", "Internal knowledge base", "title, content, category, tags"],
    ["tasks", "Assignable tasks", "title, description, status, assigned_to (FK users), due_date"],
    ["quote_items", "Line items in quotes", "quote_id (FK), description, quantity, unit_price"],
]
story.append(make_table(schema_data[0], schema_data[1:]))
story.append(PageBreak())

# ============== 8. REAL-TIME WEBSOCKET ==============
story.append(section("8. Real-Time WebSocket System"))
story.append(body(
    "MED.MIX OS includes a built-in WebSocket server for real-time multi-user synchronization. "
    "When any user creates, updates, or deletes a record, a broadcast message is sent to all "
    "connected clients, triggering an automatic data refresh."
))

story.append(subtitle("Architecture"))
story.append(body(
    "The WebSocket system is implemented in <font face='Courier' size='8'>apps/backend/app/services/realtime.py</font>. "
    "It uses a simple in-memory connection manager with a broadcast function."
))

story.append(subtitle("Connection"))
story.append(code(
    "// Connect from browser<br/>"
    "const ws = new WebSocket('wss://backend-production-40db.up.railway.app/ws');<br/>"
    "ws.onmessage = (event) => {<br/>"
    "  const msg = JSON.parse(event.data);<br/>"
    "  if (msg.event === 'data_changed') {<br/>"
    "    refreshData();<br/>"
    "  }<br/>"
    "};"
))

story.append(subtitle("Event Format"))
ws_data = [
    ["Field", "Type", "Description"],
    ["event", "string", "Always 'data_changed'"],
    ["entity_type", "string", "Affected entity (company, lead, etc.)"],
    ["entity_id", "integer", "Affected record ID"],
    ["action", "string", "Action performed (create, update, delete)"],
]
story.append(make_table(ws_data[0], ws_data[1:]))

story.append(subtitle("Frontend Integration"))
story.append(body(
    "The frontend uses a custom <font face='Courier' size='8'>useRealtime</font> hook:"
))
story.append(code(
    "import { useRealtime } from '@/lib/realtime';<br/>"
    "<br/>"
    "function MyPage() {<br/>"
    "  const [data, setData] = useState(null);<br/>"
    "  const refresh = useCallback(() => fetchData().then(setData), []);<br/>"
    "  useRealtime(refresh);  // Auto-refresh on any change<br/>"
    "  return ...;<br/>"
    "}"
))
story.append(subtitle("Auto-Reconnect"))
story.append(body(
    "The WebSocket client automatically reconnects every 3 seconds if the connection is lost. "
    "This ensures resilience against temporary network interruptions and Railway deployments."
))
story.append(PageBreak())

# ============== 9. AI ASSISTANT ==============
story.append(section("9. AI Assistant"))
story.append(body(
    "The AI Assistant provides context-aware business intelligence powered by "
    "OpenAI's GPT-4o-mini model. It loads CRM context (companies, contacts, "
    "active leads) and answers questions about the business data."
))

story.append(subtitle("How It Works"))
steps = [
    "User sends a message via the chat interface",
    "Backend loads CRM context: company/contact/lead summaries",
    "System prompt + user message sent to OpenAI API",
    "OpenAI returns a natural language response",
    "Response is streamed/sent back to the user",
]
for s in steps:
    story.append(bullet(s))

story.append(subtitle("Fallback Mode"))
story.append(body(
    "If the OpenAI API key is not configured, the assistant falls back to "
    "simple keyword-based response matching for basic queries."
))

story.append(subtitle("Configuration"))
story.append(code(
    "# Required environment variable<br/>"
    "OPENAI_API_KEY=sk-proj-...<br/>"
    "<br/>"
    "# Model: gpt-4o-mini (cheapest, $0.15/1M input tokens)<br/>"
    "# Free tier: $5 credit covers ~33,000 conversations"
))

story.append(subtitle("API Endpoint"))
api_data = [
    ["POST /api/assistant/chat", "Send message body={'message': '...'}"],
]
story.append(make_table(["Endpoint", "Usage"], api_data))

story.append(note(
    "The AI assistant only has read-only access to CRM data. It cannot create, "
    "update, or delete records."
))
story.append(PageBreak())

# ============== 10. OPENSTREETMAP ==============
story.append(section("10. OpenStreetMap Business Search"))
story.append(body(
    "MED.MIX OS includes a business data import feature powered by "
    "OpenStreetMap's Overpass API. This allows users to search for companies "
    "by type and location, completely free and without any API key."
))

story.append(subtitle("How It Works"))
steps = [
    "User specifies business type (e.g., 'restaurant', 'pharmacy', 'school')",
    "User specifies location (city or coordinates)",
    "Backend queries OpenStreetMap Overpass API for matching nodes/ways",
    "Results are parsed into lead entries in the system",
    "Optional: Google Maps fallback if GOOGLE_MAPS_API_KEY is configured",
]
for s in steps:
    story.append(bullet(s))

story.append(subtitle("API Endpoint"))
api_data = [
    ["POST /api/leads/import/search", "Body: {'query': 'restaurant', 'location': 'Riyadh'}"],
]
story.append(make_table(["Endpoint", "Usage"], api_data))

story.append(subtitle("Example Request"))
story.append(code(
    "POST /api/leads/import/search<br/>"
    "Content-Type: application/json<br/>"
    "Authorization: Bearer &lt;token&gt;<br/>"
    "<br/>"
    '{<br/>'
    '  "query": "pharmacy",<br/>'
    '  "location": "Jeddah"<br/>'
    "}"
))

story.append(subtitle("Rate Limits"))
story.append(body(
    "OpenStreetMap Overpass API has a fair use policy. For normal usage (a few "
    "searches per minute), there are no practical limits. For bulk imports, "
    "consider spacing requests 2-3 seconds apart."
))
story.append(PageBreak())

# ============== 11. FILE STORAGE ==============
story.append(section("11. File Storage"))
story.append(body(
    "MED.MIX OS uses MinIO (S3-compatible object storage) for file uploads. "
    "In production on Railway, files are stored on Railway Volumes instead."
))

story.append(subtitle("Configuration"))
story.append(code(
    "# Environment variables for file storage<br/>"
    "MINIO_ENDPOINT=localhost:9000<br/>"
    "MINIO_ACCESS_KEY=minioadmin<br/>"
    "MINIO_SECRET_KEY=minioadmin<br/>"
    "MINIO_BUCKET=medmix-files<br/>"
    "<br/>"
    "# For Railway: use local volume storage<br/>"
    "# Mount a Railway Volume at /app/uploads"
))

story.append(subtitle("Supported File Types"))
story.append(body(
    "Images (JPEG, PNG, GIF, WebP), Documents (PDF, DOCX, XLSX), and other "
    "common business file types. File size limit: 10MB per upload."
))
story.append(PageBreak())

# ============== 12. EMAIL SYSTEM ==============
story.append(section("12. Email System"))
story.append(body(
    "MED.MIX OS includes an email notification system that requires SMTP "
    "credentials to function. Currently this is an optional feature."
))

story.append(subtitle("Configuration"))
story.append(code(
    "# SMTP settings (optional)<br/>"
    "SMTP_HOST=smtp.gmail.com<br/>"
    "SMTP_PORT=587<br/>"
    "SMTP_USER=your-email@gmail.com<br/>"
    "SMTP_PASSWORD=your-app-password<br/>"
    "SMTP_FROM=noreply@medmix.com"
))

story.append(note(
    "For Gmail: Use an App Password (not your regular password). "
    "Enable 2-Step Verification first, then generate an App Password "
    "from Google Account settings."
))

story.append(subtitle("Email Features (Planned)"))
features = [
    "Welcome email on registration",
    "Password reset via email",
    "Lead assignment notifications",
    "Task deadline reminders",
    "Quote approval requests",
]
for f in features:
    story.append(bullet(f))
story.append(PageBreak())

# ============== 13. USER GUIDE (Arabic) ==============
story.append(section("13. دليل المستخدم"))

story.append(subtitle("تسجيل الدخول"))
story.append(body(
    "افتح الرابط: https://frontend-steel-three-58.vercel.app<br/>"
    "استخدم بيانات الدخول: admin@medmix.com / admin123<br/>"
    "أو سجل حساب جديد من صفحة التسجيل"
))

story.append(subtitle("لوحة التحكم"))
story.append(body(
    "تعرض لوحة التحكم نظرة عامة على أداء المبيعات: إجمالي الشركات، جهات الاتصال، "
    "العملاء المحتملين، وعروض الأسعار. كما تظهر توزيع العملاء المحتملين حسب الحالة "
    "وآخر النشاطات في النظام."
))

story.append(subtitle("إدارة العملاء (CRM)"))
story.append(body(
    "من قسم إدارة العملاء يمكنك:<br/>"
    "&bull; إضافة شركة جديدة (الاسم، الهاتف، البريد الإلكتروني، العنوان، النشاط)<br/>"
    "&bull; إضافة جهات اتصال لكل شركة<br/>"
    "&bull; إدارة المشاريع المرتبطة بكل شركة"
))

story.append(subtitle("العملاء المحتملين"))
story.append(body(
    "يمكنك تتبع العملاء المحتملين عبر مراحل البيع:<br/>"
    "&bull; جديد (NEW) &rarr; مؤهل (QUALIFIED) &rarr; تم الاتصال (CONTACTED) &rarr; قيد التفاوض "
    "(NEGOTIATING) &rarr; تم البيع (WON) / ملغي (LOST)<br/>"
    "كما يمكنك استيراد عملاء محتملين من OpenStreetMap بالبحث عن نشاط تجاري في منطقة محددة."
))

story.append(subtitle("المساعد الذكي"))
story.append(body(
    "المساعد الذكي يستطيع الإجابة على أسئلتك حول بيانات النظام. مثلاً:<br/>"
    "&bull; كم عدد العملاء المسجلين؟<br/>"
    "&bull; أرني أفضل العملاء المحتملين<br/>"
    "&bull; ما هي أحدث النشاطات؟"
))

story.append(subtitle("عروض الأسعار"))
story.append(body(
    "يمكنك إنشاء عروض أسعار للعملاء مع إضافة بنود متعددة (الوصف، الكمية، السعر). "
    "يتم حساب الإجمالي تلقائياً."
))

story.append(subtitle("المهام"))
story.append(body(
    "يمكنك إنشاء مهام وتعيينها لأعضاء الفريق مع تحديد تاريخ الاستحقاق والحالة."
))

story.append(subtitle("التحديث المباشر"))
story.append(body(
    "جميع المستخدمين يرون التغييرات فوراً. عندما يضيف أحد المستخدمين شركة جديدة "
    "أو يحدث بيانات، تظهر التغييرات لجميع المستخدمين المتصلين تلقائياً بدون تحديث الصفحة."
))
story.append(PageBreak())

# ============== 14. ENVIRONMENT VARIABLES ==============
story.append(section("14. Environment Variables"))

env_data = [
    ["Variable", "Required", "Description"],
    ["DATABASE_URL", "Yes", "PostgreSQL connection string"],
    ["SECRET_KEY", "Yes", "JWT signing secret (min 32 chars)"],
    ["OPENAI_API_KEY", "No", "OpenAI API key for AI assistant"],
    ["SMTP_HOST", "No", "SMTP server for email"],
    ["SMTP_PORT", "No", "SMTP port (usually 587)"],
    ["SMTP_USER", "No", "SMTP username/email"],
    ["SMTP_PASSWORD", "No", "SMTP password or app password"],
    ["SMTP_FROM", "No", "Sender email address"],
    ["GOOGLE_MAPS_API_KEY", "No", "Optional Google Maps fallback"],
    ["MINIO_ENDPOINT", "No", "MinIO server endpoint"],
    ["MINIO_ACCESS_KEY", "No", "MinIO access key"],
    ["MINIO_SECRET_KEY", "No", "MinIO secret key"],
    ["PORT", "No", "Server port (default: 8000)"],
    ["NEXT_PUBLIC_API_URL", "No", "Frontend: API base URL"],
]
story.append(make_table(env_data[0], env_data[1:]))
story.append(PageBreak())

# ============== 15. TROUBLESHOOTING ==============
story.append(section("15. Troubleshooting"))

story.append(subtitle("Backend Health Check"))
story.append(code(
    "curl https://backend-production-40db.up.railway.app/api/health<br/>"
    "# Expected: {\"status\":\"ok\",\"app\":\"MED.MIX OS\"}"
))

story.append(subtitle("Common Issues"))

issues_data = [
    ["Issue", "Solution"],
    ["Backend returns 502", "Wait 30s for Railway to finish deploying; check health endpoint"],
    ["Database connection failed", "Verify DATABASE_URL uses postgresql+asyncpg:// scheme"],
    ["Login returns 401", "Check username/password; ensure user is registered"],
    ["CORS error on frontend", "Verify NEXT_PUBLIC_API_URL matches backend URL; CORS configured in main.py"],
    ["WebSocket not connecting", "Ensure URL uses wss:// protocol; check Railway firewall"],
    ["AI Assistant not responding", "Verify OPENAI_API_KEY is set and has available credits"],
    ["Search returns no results", "Try broader query term; verify location name in English"],
    ["File upload fails", "Check MinIO or Railway volume configuration"],
]
story.append(make_table(issues_data[0], issues_data[1:]))

story.append(subtitle("Getting Help"))
story.append(body(
    "GitHub Repository: https://github.com/Fly89by/medmix<br/>"
    "Report issues: https://github.com/Fly89by/medmix/issues"
))

story.append(Spacer(1, 2*cm))
story.append(hr())
story.append(Paragraph(
    "MED.MIX OS v1.0 &mdash; Documentation generated June 2026",
    styles["FooterStyle"]
))

# Build
doc.build(story)
print(f"PDF generated: {OUTPUT}")
print(f"Size: {os.path.getsize(OUTPUT) / 1024:.1f} KB")
