'use client'

import { useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { api } from '@/lib/api'
import { Plus, Search, Edit, Trash2, X, BookOpen } from 'lucide-react'

interface Article { id: number; title: string; content: string; category: string; created_by: number; created_at: string }

const CATEGORIES = ['general', 'guide', 'faq', 'policy']
const catLabels: Record<string, string> = { general: 'عام', guide: 'دليل', faq: 'أسئلة شائعة', policy: 'سياسة' }
const catVariants: Record<string, 'blue' | 'green' | 'purple' | 'yellow'> = { general: 'blue', guide: 'green', faq: 'purple', policy: 'yellow' }

export default function KnowledgePage() {
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Article | null>(null)
  const [form, setForm] = useState({ title: '', content: '', category: 'general' })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const fetchArticles = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const params = new URLSearchParams()
      if (search) params.set('search', search)
      if (category) params.set('category', category)
      const data = await api.get<{ items: Article[]; total: number }>(`/knowledge?${params}`)
      setArticles(data.items)
    } catch (err: any) { setError(err.message) } finally { setLoading(false) }
  }, [search, category])

  useEffect(() => { fetchArticles() }, [fetchArticles])

  const openCreate = () => { setEditing(null); setForm({ title: '', content: '', category: 'general' }); setError(''); setModalOpen(true) }
  const openEdit = (a: Article) => { setEditing(a); setForm({ title: a.title, content: a.content, category: a.category }); setError(''); setModalOpen(true) }
  const closeModal = () => { setModalOpen(false); setEditing(null) }

  const handleSubmit = async () => {
    if (!form.title.trim() || !form.content.trim()) return
    setSaving(true); setError('')
    try {
      if (editing) await api.put(`/knowledge/${editing.id}`, form); else await api.post('/knowledge', form)
      closeModal(); fetchArticles()
    } catch (err: any) { setError(err.message) } finally { setSaving(false) }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('هل أنت متأكد؟')) return
    try { await api.delete(`/knowledge/${id}`); fetchArticles() } catch (err: any) { setError(err.message) }
  }

  return (
    <div className="space-y-6">
      <div className="page-header">
        <h1>قاعدة المعرفة</h1>
        <p>مقالات وأدلة وفريق عمل المبيعات</p>
      </div>
      {error && <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-600">{error}</div>}

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>المقالات</CardTitle>
            <Button size="sm" onClick={openCreate}><Plus className="h-4 w-4" /> إضافة مقالة</Button>
          </div>
          <div className="flex items-center gap-3 mt-3">
            <div className="relative flex-1">
              <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input type="text" placeholder="بحث..." value={search} onChange={e => setSearch(e.target.value)}
                className="w-full rounded-xl border border-gray-200 bg-white py-2.5 pr-10 pl-4 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20" />
            </div>
            <select value={category} onChange={e => setCategory(e.target.value)}
              className="rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-slate-700 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20">
              <option value="">الكل</option>
              {CATEGORIES.map(c => <option key={c} value={c}>{catLabels[c]}</option>)}
            </select>
          </div>
        </CardHeader>
        <CardContent>
          {loading && <div className="flex justify-center py-12"><div className="skeleton h-6 w-48" /></div>}
          {!loading && articles.length === 0 && (
            <div className="empty-state">
              <BookOpen className="empty-state-icon" />
              <h3>لا توجد مقالات</h3>
              <p>أضف أول مقالة في قاعدة المعرفة</p>
            </div>
          )}
          {!loading && articles.length > 0 && (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {articles.map(a => (
                <div key={a.id} className="content-card group animate-fade-in">
                  <div className="flex items-start justify-between">
                    <span className={`badge badge-${catVariants[a.category] || 'gray'}`}>{catLabels[a.category] || a.category}</span>
                    <span className="text-xs text-slate-400">{new Date(a.created_at).toLocaleDateString('ar-SA')}</span>
                  </div>
                  <h3 className="mt-3 font-semibold text-slate-900">{a.title}</h3>
                  <p className="mt-1 line-clamp-3 text-sm text-slate-500 leading-relaxed">{a.content}</p>
                  <div className="mt-4 flex items-center gap-1 pt-3 border-t border-gray-100">
                    <button onClick={() => openEdit(a)} className="rounded-lg p-1.5 text-slate-400 hover:bg-gray-100 hover:text-slate-600 transition-colors"><Edit className="h-4 w-4" /></button>
                    <button onClick={() => handleDelete(a.id)} className="rounded-lg p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-500 transition-colors"><Trash2 className="h-4 w-4" /></button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {modalOpen && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content animate-scale-in" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editing ? 'تعديل مقالة' : 'إضافة مقالة'}</h2>
              <button type="button" onClick={closeModal} className="rounded-lg p-1.5 text-slate-400 hover:bg-gray-100 hover:text-slate-600"><X className="h-5 w-5" /></button>
            </div>
            <div className="space-y-4 p-6">
              <Input label="العنوان" required value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} />
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-700">التصنيف</label>
                <select value={form.category} onChange={e => setForm({ ...form, category: e.target.value })}
                  className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-slate-900 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20">
                  {CATEGORIES.map(c => <option key={c} value={c}>{catLabels[c]}</option>)}
                </select>
              </div>
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-700">المحتوى</label>
                <textarea value={form.content} onChange={e => setForm({ ...form, content: e.target.value })}
                  className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-slate-900 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20" rows={6} />
              </div>
            </div>
            <div className="flex justify-end gap-3 border-t border-gray-100 px-6 py-4">
              <Button variant="outline" onClick={closeModal}>إلغاء</Button>
              <Button onClick={handleSubmit} disabled={!form.title.trim() || !form.content.trim() || saving}>
                {saving ? 'جاري الحفظ...' : editing ? 'حفظ التغييرات' : 'إضافة'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
