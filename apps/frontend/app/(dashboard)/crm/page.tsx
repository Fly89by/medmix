'use client'

import { useState, useEffect, useCallback, type FormEvent } from 'react'
import { Plus, Search, Edit, Trash2, X, Building2, Users, FolderKanban } from 'lucide-react'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

interface Company { id: number; name: string; industry?: string; city?: string; phone?: string; email?: string; website?: string }
interface Contact { id: number; name: string; phone?: string; email?: string; company_id?: number; company_name?: string; position?: string }
interface Project { id: number; project_name: string; company_id?: number; company_name?: string; status: string; budget?: number; city?: string }
interface PaginatedResponse<T> { items: T[]; total: number; page: number; page_size: number }

const TABS = [
  { key: 'companies', label: 'شركات', icon: Building2 },
  { key: 'contacts', label: 'جهات اتصال', icon: Users },
  { key: 'projects', label: 'مشاريع', icon: FolderKanban },
]

function Modal({ open, onClose, title, children }: { open: boolean; onClose: () => void; title: string; children: React.ReactNode }) {
  if (!open) return null
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content animate-scale-in" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{title}</h2>
          <button type="button" onClick={onClose} className="rounded-lg p-1.5 text-slate-400 hover:bg-gray-100 hover:text-slate-600 transition-colors">
            <X className="h-5 w-5" />
          </button>
        </div>
        {children}
      </div>
    </div>
  )
}

function ConfirmDialog({ open, onClose, onConfirm, title, message }: { open: boolean; onClose: () => void; onConfirm: () => void; title: string; message: string }) {
  if (!open) return null
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="animate-scale-in mx-4 w-full max-w-sm rounded-2xl border border-gray-100 bg-white p-6 shadow-2xl" onClick={e => e.stopPropagation()}>
        <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
        <p className="mt-2 text-sm text-slate-500">{message}</p>
        <div className="mt-6 flex justify-end gap-3">
          <Button variant="outline" size="sm" onClick={onClose}>إلغاء</Button>
          <Button variant="danger" size="sm" onClick={onConfirm}>تأكيد الحذف</Button>
        </div>
      </div>
    </div>
  )
}

function Select({ label, value, onChange, options, required, placeholder }: {
  label?: string; value: string; onChange: (v: string) => void; options: { value: string; label: string }[]; required?: boolean; placeholder?: string
}) {
  return (
    <div className="space-y-1.5">
      {label && <label className="block text-sm font-medium text-slate-700">{label}{required ? ' *' : ''}</label>}
      <select
        value={value} onChange={e => onChange(e.target.value)}
        className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-slate-900 transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
      >
        {placeholder && <option value="">{placeholder}</option>}
        {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  )
}

function Pagination({ page, totalPages, setPage }: { page: number; totalPages: number; setPage: (p: number) => void }) {
  if (totalPages <= 1) return null
  return (
    <div className="flex items-center justify-center gap-3 pt-4">
      <button onClick={() => setPage(page - 1)} disabled={page === 1}
        className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-slate-600 hover:bg-gray-50 disabled:opacity-40 transition-colors">السابق</button>
      <span className="text-sm text-slate-500">صفحة {page} من {totalPages}</span>
      <button onClick={() => setPage(page + 1)} disabled={page === totalPages}
        className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-slate-600 hover:bg-gray-50 disabled:opacity-40 transition-colors">التالي</button>
    </div>
  )
}

const PROJECT_STATUS_OPTIONS = [
  { value: 'NEW', label: 'جديد' }, { value: 'IN_PROGRESS', label: 'قيد التنفيذ' },
  { value: 'COMPLETED', label: 'مكتمل' }, { value: 'ON_HOLD', label: 'متوقف' }, { value: 'CANCELLED', label: 'ملغي' },
]

export default function CrmPage() {
  const [activeTab, setActiveTab] = useState('companies')
  return (
    <div className="space-y-6">
      <div className="page-header">
        <h1>إدارة العملاء</h1>
        <p>إدارة الشركات وجهات الاتصال والمشاريع</p>
      </div>
      <div className="flex gap-1 rounded-xl bg-gray-100/80 p-1">
        {TABS.map(tab => {
          const Icon = tab.icon
          return (
            <button key={tab.key} onClick={() => setActiveTab(tab.key)}
              className={`flex flex-1 items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-all ${
                activeTab === tab.key ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'
              }`}
            ><Icon className="h-4 w-4" />{tab.label}</button>
          )
        })}
      </div>
      {activeTab === 'companies' && <CrmTable<Company> endpoint="companies" fields={[
        { key: 'name', label: 'الاسم', render: (v, row) => <span className="font-medium">{v}</span> },
        { key: 'industry', label: 'النشاط' },
        { key: 'city', label: 'المدينة' },
        { key: 'phone', label: 'الهاتف' },
      ]} defaultForm={{ name: '', industry: '', city: '', phone: '', email: '', website: '' }}
        formFields={({ form, setForm }) => (<>
          <Input label="الاسم" required value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
          <Input label="النشاط" value={form.industry} onChange={e => setForm({ ...form, industry: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <Input label="المدينة" value={form.city} onChange={e => setForm({ ...form, city: e.target.value })} />
            <Input label="الهاتف" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} />
          </div>
          <Input label="البريد الإلكتروني" type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
          <Input label="الموقع الإلكتروني" value={form.website} onChange={e => setForm({ ...form, website: e.target.value })} />
        </>)} />}
      {activeTab === 'contacts' && <ContactsTable />}
      {activeTab === 'projects' && <ProjectsTable />}
    </div>
  )
}

function CrmTable<T extends { id: number }>({ endpoint, fields, defaultForm, formFields, searchable = true }: {
  endpoint: string; fields: { key: string; label: string; render?: (v: any, row: T) => React.ReactNode }[];
  defaultForm: Record<string, any>; formFields: (props: { form: Record<string, any>; setForm: (f: Record<string, any>) => void }) => React.ReactNode;
  searchable?: boolean;
}) {
  const [items, setItems] = useState<T[]>([]); const [total, setTotal] = useState(0); const [pageSize, setPageSize] = useState(10)
  const [page, setPage] = useState(1); const [searchInput, setSearchInput] = useState(''); const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true); const [error, setError] = useState('')
  const [modalOpen, setModalOpen] = useState(false); const [editing, setEditing] = useState<T | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<T | null>(null)
  const [form, setForm] = useState<Record<string, any>>(defaultForm)

  useEffect(() => { const t = setTimeout(() => { setSearch(searchInput); setPage(1) }, 400); return () => clearTimeout(t) }, [searchInput])

  const fetchData = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const params = new URLSearchParams(); if (search) params.set('search', search); params.set('page', String(page))
      const res = await api.get<PaginatedResponse<T>>(`/${endpoint}?${params}`)
      setItems(res.items); setTotal(res.total); setPageSize(res.page_size)
    } catch (e: any) { setError(e.message) } finally { setLoading(false) }
  }, [endpoint, search, page])

  useEffect(() => { fetchData() }, [fetchData])

  const openCreate = () => { setEditing(null); setForm(defaultForm); setModalOpen(true) }
  const openEdit = (item: T) => {
    setEditing(item)
    const patch: Record<string, any> = {}
    for (const k of Object.keys(defaultForm)) patch[k] = (item as any)[k] !== undefined ? (item as any)[k] : ''
    setForm(patch); setModalOpen(true)
  }
  const closeModal = () => { setModalOpen(false); setEditing(null) }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      if (editing) await api.put(`/${endpoint}/${editing.id}`, form)
      else await api.post(`/${endpoint}`, form)
      closeModal(); fetchData()
    } catch (e: any) { setError(e.message) }
  }

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try { await api.delete(`/${endpoint}/${deleteTarget.id}`); setDeleteTarget(null); if (items.length === 1 && page > 1) setPage(p => p - 1); else fetchData() }
    catch (e: any) { setError(e.message); setDeleteTarget(null) }
  }

  const totalPages = Math.ceil(total / pageSize)

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>{endpoint === 'companies' ? 'الشركات' : endpoint}</CardTitle>
          <Button size="sm" onClick={openCreate}><Plus className="h-4 w-4" /> إضافة</Button>
        </div>
        {searchable && (
          <div className="relative mt-3">
            <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input className="w-full rounded-xl border border-gray-200 bg-white py-2.5 pr-10 pl-4 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
              placeholder="بحث..." value={searchInput} onChange={e => setSearchInput(e.target.value)} />
          </div>
        )}
      </CardHeader>
      <CardContent>
        {loading && <div className="flex justify-center py-12"><div className="skeleton h-6 w-48" /></div>}
        {error && <div className="rounded-xl bg-red-50 p-4 text-sm text-red-600">{error}</div>}
        {!loading && !error && items.length === 0 && (
          <div className="empty-state">
            <Building2 className="empty-state-icon" />
            <h3>لا توجد بيانات</h3>
            <p>ابدأ بإضافة أول عنصر الآن</p>
          </div>
        )}
        {!loading && !error && items.length > 0 && (
          <div className="table-container">
            <table>
              <thead><tr>
                {fields.map(f => <th key={f.key}>{f.label}</th>)}
                <th className="w-24">الإجراءات</th>
              </tr></thead>
              <tbody>
                {items.map((item, idx) => (
                  <tr key={item.id} className="animate-fade-in" style={{ animationDelay: `${idx * 30}ms` }}>
                    {fields.map(f => (
                      <td key={f.key}>{f.render ? f.render((item as any)[f.key], item) : (item as any)[f.key] || '-'}</td>
                    ))}
                    <td>
                      <div className="flex gap-1">
                        <button onClick={() => openEdit(item)} className="rounded-lg p-1.5 text-slate-400 hover:bg-gray-100 hover:text-slate-600 transition-colors"><Edit className="h-4 w-4" /></button>
                        <button onClick={() => setDeleteTarget(item)} className="rounded-lg p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-500 transition-colors"><Trash2 className="h-4 w-4" /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <Pagination page={page} totalPages={totalPages} setPage={setPage} />
      </CardContent>
      <Modal open={modalOpen} onClose={closeModal} title={editing ? 'تعديل' : 'إضافة جديد'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="rounded-xl bg-red-50 p-3 text-sm text-red-600">{error}</div>}
          {formFields({ form, setForm })}
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="outline" type="button" onClick={closeModal}>إلغاء</Button>
            <Button type="submit">{editing ? 'حفظ التغييرات' : 'إضافة'}</Button>
          </div>
        </form>
      </Modal>
      <ConfirmDialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={handleDelete}
        title="تأكيد الحذف" message="هل أنت متأكد من حذف هذا العنصر؟" />
    </Card>
  )
}

function ContactsTable() {
  const [items, setItems] = useState<Contact[]>([]); const [total, setTotal] = useState(0); const [pageSize, setPageSize] = useState(10)
  const [page, setPage] = useState(1); const [searchInput, setSearchInput] = useState(''); const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true); const [error, setError] = useState('')
  const [modalOpen, setModalOpen] = useState(false); const [editing, setEditing] = useState<Contact | null>(null)
  const [companies, setCompanies] = useState<Company[]>([])
  const [deleteTarget, setDeleteTarget] = useState<Contact | null>(null)
  const [form, setForm] = useState({ name: '', phone: '', email: '', company_id: '', position: '' })

  useEffect(() => { const t = setTimeout(() => { setSearch(searchInput); setPage(1) }, 400); return () => clearTimeout(t) }, [searchInput])

  const fetchData = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const params = new URLSearchParams(); if (search) params.set('search', search); params.set('page', String(page))
      const res = await api.get<PaginatedResponse<Contact>>(`/contacts?${params}`)
      setItems(res.items); setTotal(res.total); setPageSize(res.page_size)
    } catch (e: any) { setError(e.message) } finally { setLoading(false) }
  }, [search, page])

  useEffect(() => { fetchData() }, [fetchData])
  useEffect(() => { if (modalOpen) api.get<PaginatedResponse<Company>>('/companies?page_size=200').then(res => setCompanies(res.items)).catch(() => setCompanies([])) }, [modalOpen])

  const closeModal = () => { setModalOpen(false); setEditing(null) }
  const handleSubmit = async (e: FormEvent) => { e.preventDefault(); try {
    const body = { name: form.name.trim(), phone: form.phone || undefined, email: form.email || undefined, company_id: form.company_id ? Number(form.company_id) : undefined, position: form.position || undefined }
    if (editing) await api.put(`/contacts/${editing.id}`, body); else await api.post('/contacts', body)
    closeModal(); fetchData()
  } catch (e: any) { setError(e.message) }}

  const handleDelete = async () => {
    if (!deleteTarget) return; try { await api.delete(`/contacts/${deleteTarget.id}`); setDeleteTarget(null); if (items.length === 1 && page > 1) setPage(p => p - 1); else fetchData() } catch (e: any) { setError(e.message); setDeleteTarget(null) }
  }

  const totalPages = Math.ceil(total / pageSize)

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>جهات الاتصال</CardTitle>
          <Button size="sm" onClick={() => { setEditing(null); setForm({ name: '', phone: '', email: '', company_id: '', position: '' }); setModalOpen(true) }}><Plus className="h-4 w-4" /> إضافة</Button>
        </div>
        <div className="relative mt-3">
          <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input className="w-full rounded-xl border border-gray-200 bg-white py-2.5 pr-10 pl-4 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
            placeholder="بحث بالاسم أو الشركة..." value={searchInput} onChange={e => setSearchInput(e.target.value)} />
        </div>
      </CardHeader>
      <CardContent>
        {loading && <div className="flex justify-center py-12"><div className="skeleton h-6 w-48" /></div>}
        {error && <div className="rounded-xl bg-red-50 p-4 text-sm text-red-600">{error}</div>}
        {!loading && !error && items.length === 0 && (
          <div className="empty-state"><Users className="empty-state-icon" /><h3>لا توجد جهات اتصال</h3><p>أضف جهة اتصال جديدة</p></div>
        )}
        {!loading && !error && items.length > 0 && (
          <div className="table-container">
            <table><thead><tr><th>الاسم</th><th>الهاتف</th><th>البريد الإلكتروني</th><th>الشركة</th><th>المنصب</th><th className="w-24">الإجراءات</th></tr></thead>
              <tbody>{items.map((item, idx) => (
                <tr key={item.id} className="animate-fade-in" style={{ animationDelay: `${idx * 30}ms` }}>
                  <td><span className="font-medium">{item.name}</span></td><td dir="ltr" className="text-left">{item.phone || '-'}</td><td dir="ltr" className="text-left text-xs">{item.email || '-'}</td>
                  <td>{item.company_name ? <Badge>{item.company_name}</Badge> : '-'}</td><td className="text-slate-500">{item.position || '-'}</td>
                  <td><div className="flex gap-1">
                    <button onClick={() => { setEditing(item); setForm({ name: item.name, phone: item.phone || '', email: item.email || '', company_id: item.company_id ? String(item.company_id) : '', position: item.position || '' }); setModalOpen(true) }} className="rounded-lg p-1.5 text-slate-400 hover:bg-gray-100 hover:text-slate-600 transition-colors"><Edit className="h-4 w-4" /></button>
                    <button onClick={() => setDeleteTarget(item)} className="rounded-lg p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-500 transition-colors"><Trash2 className="h-4 w-4" /></button>
                  </div></td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        )}
        <Pagination page={page} totalPages={totalPages} setPage={setPage} />
      </CardContent>
      <Modal open={modalOpen} onClose={closeModal} title={editing ? 'تعديل جهة اتصال' : 'إضافة جهة اتصال'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="rounded-xl bg-red-50 p-3 text-sm text-red-600">{error}</div>}
          <Input label="الاسم" required value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
          <div className="grid grid-cols-2 gap-3"><Input label="الهاتف" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} />
          <Input label="البريد الإلكتروني" type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} /></div>
          <Select label="الشركة" value={form.company_id} onChange={v => setForm({ ...form, company_id: v })} options={companies.map(c => ({ value: String(c.id), label: c.name }))} placeholder="اختر الشركة" />
          <Input label="المنصب" value={form.position} onChange={e => setForm({ ...form, position: e.target.value })} />
          <div className="flex justify-end gap-3 pt-2"><Button variant="outline" type="button" onClick={closeModal}>إلغاء</Button><Button type="submit">{editing ? 'حفظ' : 'إضافة'}</Button></div>
        </form>
      </Modal>
      <ConfirmDialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={handleDelete} title="تأكيد الحذف" message="هل أنت متأكد من حذف جهة الاتصال هذه؟" />
    </Card>
  )
}

function ProjectsTable() {
  const [items, setItems] = useState<Project[]>([]); const [total, setTotal] = useState(0); const [pageSize, setPageSize] = useState(10)
  const [page, setPage] = useState(1); const [searchInput, setSearchInput] = useState(''); const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true); const [error, setError] = useState('')
  const [modalOpen, setModalOpen] = useState(false); const [editing, setEditing] = useState<Project | null>(null)
  const [companies, setCompanies] = useState<Company[]>([])
  const [deleteTarget, setDeleteTarget] = useState<Project | null>(null)
  const [form, setForm] = useState({ project_name: '', company_id: '', status: 'NEW', budget: '' })

  useEffect(() => { const t = setTimeout(() => { setSearch(searchInput); setPage(1) }, 400); return () => clearTimeout(t) }, [searchInput])

  const fetchData = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const params = new URLSearchParams(); if (search) params.set('search', search); params.set('page', String(page))
      const res = await api.get<PaginatedResponse<Project>>(`/projects?${params}`)
      setItems(res.items); setTotal(res.total); setPageSize(res.page_size)
    } catch (e: any) { setError(e.message) } finally { setLoading(false) }
  }, [search, page])

  useEffect(() => { fetchData() }, [fetchData])
  useEffect(() => { if (modalOpen) api.get<PaginatedResponse<Company>>('/companies?page_size=200').then(res => setCompanies(res.items)).catch(() => setCompanies([])) }, [modalOpen])

  const closeModal = () => { setModalOpen(false); setEditing(null) }
  const handleSubmit = async (e: FormEvent) => { e.preventDefault(); try {
    const body = { project_name: form.project_name.trim(), company_id: form.company_id ? Number(form.company_id) : undefined, status: form.status, budget: form.budget ? Number(form.budget) : undefined }
    if (editing) await api.put(`/projects/${editing.id}`, body); else await api.post('/projects', body)
    closeModal(); fetchData()
  } catch (e: any) { setError(e.message) }}

  const handleDelete = async () => { if (!deleteTarget) return; try { await api.delete(`/projects/${deleteTarget.id}`); setDeleteTarget(null); if (items.length === 1 && page > 1) setPage(p => p - 1); else fetchData() } catch (e: any) { setError(e.message); setDeleteTarget(null) }}

  const totalPages = Math.ceil(total / pageSize)

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>المشاريع</CardTitle>
          <Button size="sm" onClick={() => { setEditing(null); setForm({ project_name: '', company_id: '', status: 'NEW', budget: '' }); setModalOpen(true) }}><Plus className="h-4 w-4" /> إضافة</Button>
        </div>
        <div className="relative mt-3">
          <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input className="w-full rounded-xl border border-gray-200 bg-white py-2.5 pr-10 pl-4 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
            placeholder="بحث..." value={searchInput} onChange={e => setSearchInput(e.target.value)} />
        </div>
      </CardHeader>
      <CardContent>
        {loading && <div className="flex justify-center py-12"><div className="skeleton h-6 w-48" /></div>}
        {error && <div className="rounded-xl bg-red-50 p-4 text-sm text-red-600">{error}</div>}
        {!loading && !error && items.length === 0 && <div className="empty-state"><FolderKanban className="empty-state-icon" /><h3>لا توجد مشاريع</h3><p>أضف مشروعاً جديداً</p></div>}
        {!loading && !error && items.length > 0 && (
          <div className="table-container">
            <table><thead><tr><th>اسم المشروع</th><th>الشركة</th><th>الحالة</th><th>الميزانية</th><th className="w-24">الإجراءات</th></tr></thead>
              <tbody>{items.map((item, idx) => (
                <tr key={item.id} className="animate-fade-in" style={{ animationDelay: `${idx * 30}ms` }}>
                  <td><span className="font-medium">{item.project_name}</span></td><td>{item.company_name ? <Badge>{item.company_name}</Badge> : '-'}</td>
                  <td><Badge>{item.status}</Badge></td><td>{item.budget ? `${Number(item.budget).toLocaleString()} ر.س` : '-'}</td>
                  <td><div className="flex gap-1">
                    <button onClick={() => { setEditing(item); setForm({ project_name: item.project_name, company_id: item.company_id ? String(item.company_id) : '', status: item.status, budget: item.budget ? String(item.budget) : '' }); setModalOpen(true) }} className="rounded-lg p-1.5 text-slate-400 hover:bg-gray-100 hover:text-slate-600 transition-colors"><Edit className="h-4 w-4" /></button>
                    <button onClick={() => setDeleteTarget(item)} className="rounded-lg p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-500 transition-colors"><Trash2 className="h-4 w-4" /></button>
                  </div></td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        )}
        <Pagination page={page} totalPages={totalPages} setPage={setPage} />
      </CardContent>
      <Modal open={modalOpen} onClose={closeModal} title={editing ? 'تعديل المشروع' : 'إضافة مشروع'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="rounded-xl bg-red-50 p-3 text-sm text-red-600">{error}</div>}
          <Input label="اسم المشروع" required value={form.project_name} onChange={e => setForm({ ...form, project_name: e.target.value })} />
          <Select label="الشركة" value={form.company_id} onChange={v => setForm({ ...form, company_id: v })} options={companies.map(c => ({ value: String(c.id), label: c.name }))} placeholder="اختر الشركة" />
          <Select label="الحالة" value={form.status} onChange={v => setForm({ ...form, status: v })} options={PROJECT_STATUS_OPTIONS} />
          <Input label="الميزانية" type="number" value={form.budget} onChange={e => setForm({ ...form, budget: e.target.value })} />
          <div className="flex justify-end gap-3 pt-2"><Button variant="outline" type="button" onClick={closeModal}>إلغاء</Button><Button type="submit">{editing ? 'حفظ' : 'إضافة'}</Button></div>
        </form>
      </Modal>
      <ConfirmDialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={handleDelete} title="تأكيد الحذف" message="هل أنت متأكد من حذف هذا المشروع؟" />
    </Card>
  )
}
