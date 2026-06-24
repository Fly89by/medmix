'use client'

import { useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { api } from '@/lib/api'
import { Plus, Search, Edit, Trash2, FileText, X } from 'lucide-react'

interface Quote { id: number; quote_number: string; customer_name: string; customer_phone: string; customer_email: string; product: string; quantity: number; unit_price: number; total_price: number; city: string; notes: string; status: string; created_at: string }
interface PageData { items: Quote[]; total: number; page: number; page_size: number }

const emptyForm = { customer_name: '', customer_phone: '', customer_email: '', product: '', quantity: '', unit_price: '', city: '', notes: '' }

const statusOptions = [
  { value: '', label: 'الكل' }, { value: 'DRAFT', label: 'مسودة' }, { value: 'SENT', label: 'مرسل' },
  { value: 'ACCEPTED', label: 'مقبول' }, { value: 'REJECTED', label: 'مرفوض' }, { value: 'EXPIRED', label: 'منتهي' },
]

const statusLabelMap: Record<string, string> = { DRAFT: 'مسودة', SENT: 'مرسل', ACCEPTED: 'مقبول', REJECTED: 'مرفوض', EXPIRED: 'منتهي' }

function formatCurrency(amount: number) { return amount.toLocaleString('ar-SA') }
function formatDate(dateStr: string) { return new Date(dateStr).toLocaleDateString('ar-SA', { year: 'numeric', month: 'short', day: 'numeric' }) }

export default function QuotesPage() {
  const [items, setItems] = useState<Quote[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Quote | null>(null)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)

  useEffect(() => { const t = setTimeout(() => { setSearch(searchInput); setPage(1) }, 400); return () => clearTimeout(t) }, [searchInput])

  const fetchData = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const params = new URLSearchParams()
      if (search) params.set('search', search)
      if (statusFilter) params.set('status', statusFilter)
      params.set('page', String(page))
      const res = await api.get<PageData>(`/quotes?${params}`)
      setItems(res.items); setTotal(res.total); setPageSize(res.page_size)
    } catch (e: any) { setError(e.message) } finally { setLoading(false) }
  }, [search, statusFilter, page])

  useEffect(() => { fetchData() }, [fetchData])

  const totalPages = Math.ceil(total / pageSize)
  const totalPrice = (Number(form.quantity) || 0) * (Number(form.unit_price) || 0)
  const isFormValid = form.customer_name.trim() && form.product.trim() && Number(form.quantity) > 0 && Number(form.unit_price) > 0

  const openCreate = () => { setEditing(null); setForm(emptyForm); setError(''); setModalOpen(true) }
  const openEdit = (q: Quote) => { setEditing(q); setForm({ customer_name: q.customer_name, customer_phone: q.customer_phone, customer_email: q.customer_email, product: q.product, quantity: String(q.quantity), unit_price: String(q.unit_price), city: q.city, notes: q.notes }); setModalOpen(true) }
  const closeModal = () => { setModalOpen(false); setEditing(null); setForm(emptyForm); setError('') }

  const handleSubmit = async () => {
    if (!isFormValid) return; setSaving(true); setError('')
    try {
      const body = { customer_name: form.customer_name, customer_phone: form.customer_phone || undefined, customer_email: form.customer_email || undefined, product: form.product, quantity: Number(form.quantity), unit_price: Number(form.unit_price), city: form.city || undefined, notes: form.notes || undefined }
      if (editing) await api.put(`/quotes/${editing.id}`, body); else await api.post('/quotes', body)
      closeModal(); fetchData()
    } catch (e: any) { setError(e.message) } finally { setSaving(false) }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('هل أنت متأكد من حذف عرض السعر هذا؟')) return
    try { await api.delete(`/quotes/${id}`); if (items.length === 1 && page > 1) setPage(p => p - 1); else fetchData() } catch (e: any) { setError(e.message) }
  }

  const handleDownloadPdf = async (id: number) => {
    try {
      const token = localStorage.getItem('token')
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'
      const res = await fetch(`${API_URL}/quotes/${id}/pdf`, { headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) } })
      if (!res.ok) throw new Error('Failed to download PDF')
      const blob = await res.blob(); const url = URL.createObjectURL(blob); window.open(url, '_blank')
    } catch (e: any) { setError(e.message) }
  }

  return (
    <div className="space-y-6">
      <div className="page-header">
        <h1>عروض الأسعار</h1>
        <p>إنشاء وإدارة عروض الأسعار للعملاء</p>
      </div>
      {error && <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-600">{error}</div>}

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>جميع عروض الأسعار</CardTitle>
            <Button size="sm" onClick={openCreate}><Plus className="h-4 w-4" /> إنشاء</Button>
          </div>
          <div className="flex items-center gap-3 mt-3">
            <div className="relative flex-1">
              <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input type="text" placeholder="بحث باسم العميل..." value={searchInput} onChange={e => setSearchInput(e.target.value)}
                className="w-full rounded-xl border border-gray-200 bg-white py-2.5 pr-10 pl-4 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20" />
            </div>
            <select value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setPage(1) }}
              className="rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-slate-700 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20">
              {statusOptions.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {loading && <div className="flex justify-center py-12"><div className="skeleton h-6 w-48" /></div>}
          {!loading && !error && items.length === 0 && (
            <div className="empty-state">
              <FileText className="empty-state-icon" />
              <h3>لا توجد عروض أسعار</h3>
              <p>أنشئ أول عرض سعر الآن</p>
            </div>
          )}
          {!loading && !error && items.length > 0 && (
            <div className="table-container">
              <table>
                <thead><tr><th>#</th><th>العميل</th><th>المنتج</th><th>المبلغ</th><th>الحالة</th><th>التاريخ</th><th className="w-32">الإجراءات</th></tr></thead>
                <tbody>
                  {items.map((q, idx) => (
                    <tr key={q.id} className="animate-fade-in" style={{ animationDelay: `${idx * 30}ms` }}>
                      <td><span className="font-medium text-primary">{q.quote_number}</span></td>
                      <td className="font-medium">{q.customer_name}</td>
                      <td className="text-slate-500">{q.product}</td>
                      <td className="font-medium">{formatCurrency(q.total_price)} ر.س</td>
                      <td><Badge>{q.status}</Badge></td>
                      <td className="text-slate-500 text-xs">{formatDate(q.created_at)}</td>
                      <td>
                        <div className="flex gap-1">
                          <button onClick={() => openEdit(q)} className="rounded-lg p-1.5 text-slate-400 hover:bg-gray-100 hover:text-slate-600"><Edit className="h-4 w-4" /></button>
                          <button onClick={() => handleDownloadPdf(q.id)} className="rounded-lg p-1.5 text-slate-400 hover:bg-gray-100 hover:text-slate-600"><FileText className="h-4 w-4" /></button>
                          <button onClick={() => handleDelete(q.id)} className="rounded-lg p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-500"><Trash2 className="h-4 w-4" /></button>
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
              <span>إجمالي {total} عرض سعر</span>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(p => Math.max(1, p - 1))}>السابق</Button>
                <span>صفحة {page} من {totalPages}</span>
                <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>التالي</Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {modalOpen && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content animate-scale-in" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editing ? 'تعديل عرض سعر' : 'إنشاء عرض سعر'}</h2>
              <button type="button" onClick={closeModal} className="rounded-lg p-1.5 text-slate-400 hover:bg-gray-100 hover:text-slate-600"><X className="h-5 w-5" /></button>
            </div>
            <div className="space-y-4 p-6">
              <Input label="اسم العميل *" value={form.customer_name} onChange={e => setForm({ ...form, customer_name: e.target.value })} />
              <div className="grid grid-cols-2 gap-3">
                <Input label="رقم الجوال" value={form.customer_phone} onChange={e => setForm({ ...form, customer_phone: e.target.value })} />
                <Input label="البريد الإلكتروني" type="email" value={form.customer_email} onChange={e => setForm({ ...form, customer_email: e.target.value })} />
              </div>
              <Input label="المنتج *" value={form.product} onChange={e => setForm({ ...form, product: e.target.value })} />
              <div className="grid grid-cols-2 gap-3">
                <Input label="الكمية *" type="number" value={form.quantity} onChange={e => setForm({ ...form, quantity: e.target.value })} />
                <Input label="سعر الوحدة *" type="number" value={form.unit_price} onChange={e => setForm({ ...form, unit_price: e.target.value })} />
              </div>
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-700">الإجمالي</label>
                <div className="rounded-xl border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm text-slate-900 font-medium">{formatCurrency(totalPrice)} ر.س</div>
              </div>
              <Input label="المدينة" value={form.city} onChange={e => setForm({ ...form, city: e.target.value })} />
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-700">ملاحظات</label>
                <textarea value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })}
                  className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-slate-900 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20" rows={3} />
              </div>
            </div>
            <div className="flex justify-end gap-3 border-t border-gray-100 px-6 py-4">
              <Button variant="outline" onClick={closeModal}>إلغاء</Button>
              <Button onClick={handleSubmit} disabled={!isFormValid || saving}>{saving ? 'جاري الحفظ...' : editing ? 'حفظ التغييرات' : 'إنشاء'}</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
