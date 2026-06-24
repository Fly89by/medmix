'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Plus, Search, Edit, Trash2, X, MapPin, Upload, Download, Loader2, Building2, Globe, Star } from 'lucide-react'

interface Lead { id: number; company_name: string; industry: string; city: string; phone: string; email: string; website: string; source: string; status: string; score: number; assigned_to: string | null; notes: string; created_at: string }
interface PageData { items: Lead[]; total: number; page: number; page_size: number }
interface GoogleResult { company_name: string; industry: string; city: string; phone: string; email: string; website: string; rating?: number; address?: string }

const STATUS_LABELS: Record<string, string> = { NEW: 'جديد', QUALIFIED: 'مؤهل', CONTACTED: 'تم الاتصال', NEGOTIATING: 'قيد التفاوض', WON: 'تم البيع', LOST: 'ملغي' }
const STATUS_TRANSITIONS: Record<string, string[]> = { NEW: ['QUALIFIED', 'LOST'], QUALIFIED: ['CONTACTED', 'LOST'], CONTACTED: ['NEGOTIATING', 'LOST'], NEGOTIATING: ['WON', 'LOST'], WON: [], LOST: [] }
const defaultForm = { company_name: '', industry: '', city: '', phone: '', email: '', website: '', source: 'manual', notes: '' }

function getScoreBadge(score: number) {
  if (score < 30) return <Badge variant="gray">{score}</Badge>
  if (score <= 50) return <Badge variant="yellow">{score}</Badge>
  if (score <= 75) return <Badge variant="blue">{score}</Badge>
  return <Badge variant="green">{score}</Badge>
}

export default function LeadsPage() {
  const [items, setItems] = useState<Lead[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // CRUD modal
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Lead | null>(null)
  const [form, setForm] = useState(defaultForm)
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  // Google Maps search
  const [mapsOpen, setMapsOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchLocation, setSearchLocation] = useState('')
  const [searching, setSearching] = useState(false)
  const [searchResults, setSearchResults] = useState<GoogleResult[]>([])
  const [selectedResults, setSelectedResults] = useState<Set<number>>(new Set())
  const [importingSelected, setImportingSelected] = useState(false)

  // CSV import
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [csvImporting, setCsvImporting] = useState(false)

  useEffect(() => { const t = setTimeout(() => { setSearch(searchInput); setPage(1) }, 400); return () => clearTimeout(t) }, [searchInput])

  const fetchData = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const params = new URLSearchParams()
      if (search) params.set('search', search)
      if (statusFilter) params.set('status', statusFilter)
      params.set('page', String(page))
      const res = await api.get<PageData>(`/leads?${params}`)
      setItems(res.items); setTotal(res.total); setPageSize(res.page_size)
    } catch (e: any) { setError(e.message) } finally { setLoading(false) }
  }, [search, statusFilter, page])

  useEffect(() => { fetchData() }, [fetchData])

  const totalPages = Math.ceil(total / pageSize)

  const openCreate = () => { setEditing(null); setForm(defaultForm); setFormError(''); setModalOpen(true) }
  const openEdit = (lead: Lead) => { setEditing(lead); setForm({ company_name: lead.company_name, industry: lead.industry, city: lead.city, phone: lead.phone, email: lead.email, website: lead.website, source: lead.source, notes: lead.notes || '' }); setFormError(''); setModalOpen(true) }
  const closeModal = () => { setModalOpen(false); setEditing(null) }
  const handleSubmit = async () => {
    if (!form.company_name.trim()) { setFormError('اسم الشركة مطلوب'); return }
    setSubmitting(true); setFormError('')
    try { if (editing) await api.put(`/leads/${editing.id}`, form); else await api.post('/leads', form); closeModal(); fetchData() } catch (e: any) { setFormError(e.message) } finally { setSubmitting(false) }
  }

  const handleStatusChange = async (leadId: number, newStatus: string) => {
    try { await api.put(`/leads/${leadId}`, { status: newStatus }); fetchData() } catch (e: any) { setError(e.message) }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('هل أنت متأكد من حذف هذا العميل المتوقع؟')) return
    try { await api.delete(`/leads/${id}`); if (items.length === 1 && page > 1) setPage(p => p - 1); else fetchData() } catch (e: any) { setError(e.message) }
  }

  // Google Maps search
  const handleGoogleSearch = async () => {
    if (!searchQuery.trim()) return
    setSearching(true); setSearchResults([])
    try {
      const res = await api.post<{ results: GoogleResult[]; total: number; mode: string }>('/leads/import/google-maps', { query: searchQuery, location: searchLocation || undefined, max_results: 12 })
      setSearchResults(res.results)
    } catch (e: any) { setError(e.message) } finally { setSearching(false) }
  }

  const toggleResult = (idx: number) => {
    setSelectedResults(prev => {
      const next = new Set(prev)
      if (next.has(idx)) next.delete(idx); else next.add(idx)
      return next
    })
  }

  const importSelected = async () => {
    if (selectedResults.size === 0) return
    setImportingSelected(true)
    try {
      const leadsToImport = searchResults.filter((_, i) => selectedResults.has(i))
      await api.post('/leads/import/bulk', { leads: leadsToImport })
      setMapsOpen(false); setSearchResults([]); setSelectedResults(new Set()); setSearchQuery(''); setSearchLocation('')
      fetchData()
    } catch (e: any) { setError(e.message) } finally { setImportingSelected(false) }
  }

  const openMaps = () => {
    setMapsOpen(true); setSearchResults([]); setSelectedResults(new Set()); setSearchQuery(''); setSearchLocation('')
  }

  // CSV import
  const handleCsvFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setCsvImporting(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const token = localStorage.getItem('token')
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'
      const res = await fetch(`${API_URL}/leads/import/csv`, {
        method: 'POST',
        headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        body: formData,
      })
      if (!res.ok) { const err = await res.json(); throw new Error(err.detail || err.message) }
      const data = await res.json()
      fetchData()
    } catch (e: any) { setError(e.message) } finally { setCsvImporting(false); if (fileInputRef.current) fileInputRef.current.value = '' }
  }

  const downloadCsvTemplate = () => {
    const csv = `company_name,industry,city,phone,email,website,notes\nشركة الأمل للتجارة,Retail,الرياض,0550000000,info@alamal.com,https://alamal.com,عميل محتمل\n`
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = 'lead-import-template.csv'; a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      <div className="page-header">
        <h1>العملاء المتوقعون</h1>
        <p>إدارة وتتبع العملاء المتوقعين وفرص البيع</p>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Button size="sm" onClick={openCreate}><Plus className="h-4 w-4" /> إضافة</Button>
          <Button size="sm" variant="outline" onClick={openMaps}><MapPin className="h-4 w-4" /> بحث Google Maps</Button>
          <input ref={fileInputRef} type="file" accept=".csv" className="hidden" onChange={handleCsvFile} />
          <Button size="sm" variant="outline" onClick={() => fileInputRef.current?.click()} disabled={csvImporting}>
            {csvImporting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
            CSV
          </Button>
          <Button size="sm" variant="ghost" onClick={downloadCsvTemplate}><Download className="h-4 w-4" /> نموذج</Button>
        </div>
        <div className="flex items-center gap-2">
          <select value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setPage(1) }}
            className="rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-slate-700 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20">
            <option value="">كل الحالات</option>
            {Object.entries(STATUS_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
          <div className="relative w-56">
            <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input placeholder="بحث..." value={searchInput} onChange={e => setSearchInput(e.target.value)}
              className="w-full rounded-xl border border-gray-200 bg-white py-2.5 pr-10 pl-4 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20" />
          </div>
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          {loading && <div className="flex justify-center py-12"><div className="skeleton h-6 w-48" /></div>}
          {error && <div className="rounded-xl bg-red-50 p-4 text-sm text-red-600 m-4">{error}</div>}
          {!loading && !error && items.length === 0 && (
            <div className="empty-state">
              <Building2 className="empty-state-icon" />
              <h3>لا توجد نتائج</h3>
              <p>أضف عميلاً متوقعاً جديداً أو استخدم Google Maps للبحث</p>
            </div>
          )}
          {!loading && !error && items.length > 0 && (
            <div className="table-container">
              <table>
                <thead><tr>
                  <th>الشركة</th><th>المدينة</th><th>الهاتف</th><th>الدرجة</th><th>المصدر</th><th>الحالة</th><th className="w-36">الإجراءات</th>
                </tr></thead>
                <tbody>
                  {items.map((lead, idx) => (
                    <tr key={lead.id} className="animate-fade-in" style={{ animationDelay: `${idx * 30}ms` }}>
                      <td>
                        <div>
                          <span className="font-medium">{lead.company_name}</span>
                          {lead.industry && <span className="block text-xs text-slate-400">{lead.industry}</span>}
                        </div>
                      </td>
                      <td className="text-slate-500">{lead.city || '-'}</td>
                      <td className="text-slate-500 text-left" dir="ltr">{lead.phone || '-'}</td>
                      <td>{getScoreBadge(lead.score)}</td>
                      <td><Badge variant="gray">{lead.source === 'google_maps' ? 'Google Maps' : lead.source === 'csv_import' ? 'CSV' : lead.source}</Badge></td>
                      <td><Badge>{lead.status}</Badge></td>
                      <td>
                        <div className="flex items-center gap-1">
                          <button onClick={() => openEdit(lead)} className="rounded-lg p-1.5 text-slate-400 hover:bg-gray-100 hover:text-slate-600"><Edit className="h-4 w-4" /></button>
                          {STATUS_TRANSITIONS[lead.status]?.length > 0 && (
                            <select value="" onChange={e => e.target.value && handleStatusChange(lead.id, e.target.value)}
                              className="rounded-lg border border-gray-200 px-1.5 py-1 text-xs bg-white text-slate-500">
                              <option value="">تغيير</option>
                              {STATUS_TRANSITIONS[lead.status].map(s => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
                            </select>
                          )}
                          <button onClick={() => handleDelete(lead.id)} className="rounded-lg p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-500"><Trash2 className="h-4 w-4" /></button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {total > 0 && (
            <div className="flex items-center justify-between border-t border-gray-100 px-6 py-3 text-sm text-slate-500">
              <span>إجمالي {total} · صفحة {page} من {totalPages || 1}</span>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(p => Math.max(1, p - 1))}>السابق</Button>
                <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>التالي</Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Google Maps Search Modal */}
      {mapsOpen && (
        <div className="modal-overlay" onClick={() => setMapsOpen(false)}>
          <div className="modal-content animate-scale-in max-w-2xl" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>بحث Google Maps</h2>
              <button type="button" onClick={() => setMapsOpen(false)} className="rounded-lg p-1.5 text-slate-400 hover:bg-gray-100 hover:text-slate-600"><X className="h-5 w-5" /></button>
            </div>
            <div className="p-6">
              <div className="flex items-end gap-3 mb-4">
                <div className="flex-1">
                  <Input label="نشاط تجاري" placeholder="مثال: مطاعم، مقاولات، صيدليات..." value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleGoogleSearch()} />
                </div>
                <div className="w-40">
                  <Input label="الموقع" placeholder="اختياري" value={searchLocation} onChange={e => setSearchLocation(e.target.value)} />
                </div>
                <Button onClick={handleGoogleSearch} disabled={!searchQuery.trim() || searching}>
                  {searching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                  بحث
                </Button>
              </div>

              {searching && (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-primary" />
                  <span className="mr-2 text-sm text-slate-500">جاري البحث...</span>
                </div>
              )}

              {!searching && searchResults.length > 0 && (
                <>
                  <p className="mb-3 text-sm text-slate-500">تم العثور على {searchResults.length} نتيجة</p>
                  <div className="max-h-80 space-y-2 overflow-y-auto">
                    {searchResults.map((r, i) => (
                      <div key={i} onClick={() => toggleResult(i)}
                        className={`flex cursor-pointer items-start gap-3 rounded-xl border p-3 transition-all ${
                          selectedResults.has(i) ? 'border-primary bg-primary/5 ring-1 ring-primary' : 'border-gray-100 hover:border-gray-200 hover:bg-gray-50'
                        }`}>
                        <div className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded border-2 transition-colors ${
                          selectedResults.has(i) ? 'border-primary bg-primary text-white' : 'border-gray-300'
                        }`}>
                          {selectedResults.has(i) && <span className="text-xs font-bold">✓</span>}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <h4 className="font-medium text-slate-900 truncate">{r.company_name}</h4>
                            {r.rating && <span className="flex items-center gap-1 text-xs text-yellow-500"><Star className="h-3 w-3 fill-current" />{r.rating}</span>}
                          </div>
                          <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-500">
                            {r.industry && <span>{r.industry}</span>}
                            {r.city && <span>• {r.city}</span>}
                            {r.phone && <span dir="ltr">• {r.phone}</span>}
                          </div>
                          {r.address && <p className="mt-0.5 text-xs text-slate-400 truncate">{r.address}</p>}
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 flex items-center justify-between border-t border-gray-100 pt-4">
                    <span className="text-sm text-slate-500">تم اختيار {selectedResults.size} من {searchResults.length}</span>
                    <Button onClick={importSelected} disabled={selectedResults.size === 0 || importingSelected}>
                      {importingSelected ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                      استيراد المحدد
                    </Button>
                  </div>
                </>
              )}

              {!searching && searchResults.length === 0 && searchQuery && (
                <div className="py-8 text-center text-slate-400">لا توجد نتائج. جرب كلمة بحث مختلفة.</div>
              )}

              {!searching && searchResults.length === 0 && !searchQuery && (
                <div className="flex flex-col items-center py-8 text-slate-400">
                  <MapPin className="h-12 w-12 mb-2 opacity-50" />
                  <p className="text-sm">ابحث عن شركات وعملاء باستخدام Google Maps</p>
                  <p className="text-xs mt-1">مثال: أدخل "مطاعم" و"الرياض" للبحث عن مطاعم في الرياض</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* CRUD Modal */}
      {modalOpen && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content animate-scale-in" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editing ? 'تعديل عميل متوقع' : 'إضافة عميل متوقع'}</h2>
              <button type="button" onClick={closeModal} className="rounded-lg p-1.5 text-slate-400 hover:bg-gray-100 hover:text-slate-600"><X className="h-5 w-5" /></button>
            </div>
            <div className="space-y-4 p-6">
              {formError && <div className="rounded-xl bg-red-50 p-3 text-sm text-red-600">{formError}</div>}
              <Input label="اسم الشركة" required value={form.company_name} onChange={e => setForm({ ...form, company_name: e.target.value })} />
              <div className="grid grid-cols-2 gap-3">
                <Input label="النشاط" value={form.industry} onChange={e => setForm({ ...form, industry: e.target.value })} />
                <Input label="المدينة" value={form.city} onChange={e => setForm({ ...form, city: e.target.value })} />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <Input label="رقم الهاتف" type="tel" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} />
                <Input label="البريد الإلكتروني" type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
              </div>
              <Input label="الموقع الإلكتروني" type="url" value={form.website} onChange={e => setForm({ ...form, website: e.target.value })} />
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-700">ملاحظات</label>
                <textarea value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })}
                  className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-slate-900 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20" rows={3} />
              </div>
            </div>
            <div className="flex justify-end gap-3 border-t border-gray-100 px-6 py-4">
              <Button variant="outline" onClick={closeModal}>إلغاء</Button>
              <Button onClick={handleSubmit} disabled={submitting}>{submitting ? 'جاري الحفظ...' : editing ? 'حفظ التغييرات' : 'إضافة'}</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
