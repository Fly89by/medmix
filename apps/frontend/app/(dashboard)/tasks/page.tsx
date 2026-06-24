'use client'

import { useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { api } from '@/lib/api'
import { Plus, X, CheckCircle2, Circle } from 'lucide-react'

interface Task { id: number; title: string; description?: string; related_type?: string; related_id?: number; assigned_to?: number; status: string; due_date?: string; completed_at?: string; created_at: string }

const statusLabels: Record<string, string> = { pending: 'معلق', in_progress: 'قيد التنفيذ', completed: 'مكتمل' }

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Task | null>(null)
  const [form, setForm] = useState({ title: '', description: '', status: 'pending' })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const fetchTasks = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const params = new URLSearchParams()
      if (statusFilter) params.set('status', statusFilter)
      const data = await api.get<{ items: Task[]; total: number }>(`/tasks?${params}`)
      setTasks(data.items)
    } catch (err: any) { setError(err.message) } finally { setLoading(false) }
  }, [statusFilter])

  useEffect(() => { fetchTasks() }, [fetchTasks])

  const openCreate = () => { setEditing(null); setForm({ title: '', description: '', status: 'pending' }); setError(''); setModalOpen(true) }
  const openEdit = (t: Task) => { setEditing(t); setForm({ title: t.title, description: t.description || '', status: t.status }); setError(''); setModalOpen(true) }
  const closeModal = () => { setModalOpen(false); setEditing(null) }

  const handleSubmit = async () => {
    if (!form.title.trim()) return
    setSaving(true); setError('')
    try {
      if (editing) await api.put(`/tasks/${editing.id}`, form); else await api.post('/tasks', form)
      closeModal(); fetchTasks()
    } catch (err: any) { setError(err.message) } finally { setSaving(false) }
  }

  const toggleComplete = async (t: Task) => {
    const newStatus = t.status === 'completed' ? 'pending' : 'completed'
    try { await api.put(`/tasks/${t.id}`, { status: newStatus }); fetchTasks() } catch (err: any) { setError(err.message) }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('هل أنت متأكد؟')) return
    try { await api.delete(`/tasks/${id}`); fetchTasks() } catch (err: any) { setError(err.message) }
  }

  const openCount = tasks.filter(t => t.status !== 'completed').length
  const completedCount = tasks.filter(t => t.status === 'completed').length

  return (
    <div className="space-y-6">
      <div className="page-header">
        <h1>المهام</h1>
        <p>إدارة ومتابعة مهام فريق العمل</p>
      </div>
      {error && <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-600">{error}</div>}

      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-4 py-2 shadow-sm">
            <Circle className="h-4 w-4 text-primary" />
            <span className="text-sm text-slate-600">المفتوحة: <strong className="text-slate-900">{openCount}</strong></span>
          </div>
          <div className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-4 py-2 shadow-sm">
            <CheckCircle2 className="h-4 w-4 text-green-500" />
            <span className="text-sm text-slate-600">المكتملة: <strong className="text-slate-900">{completedCount}</strong></span>
          </div>
        </div>
        <Button size="sm" onClick={openCreate}><Plus className="h-4 w-4" /> إضافة مهمة</Button>
      </div>

      <div className="flex items-center gap-3">
        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)}
          className="rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-slate-700 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20">
          <option value="">جميع المهام</option>
          {Object.entries(statusLabels).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
      </div>

      {loading && <div className="flex justify-center py-12"><div className="skeleton h-6 w-48" /></div>}
      {!loading && tasks.length === 0 && (
        <div className="empty-state">
          <Circle className="empty-state-icon" />
          <h3>لا توجد مهام</h3>
          <p>أضف أول مهمة الآن</p>
        </div>
      )}
      {!loading && tasks.length > 0 && (
        <div className="space-y-3">
          {tasks.map((t, idx) => (
            <div key={t.id} className={`content-card animate-fade-in flex items-start gap-4 p-4 transition-all ${t.status === 'completed' ? 'opacity-60' : ''}`} style={{ animationDelay: `${idx * 30}ms` }}>
              <button onClick={() => toggleComplete(t)} className="mt-0.5 shrink-0 text-slate-300 hover:text-green-500 transition-colors">
                {t.status === 'completed' ? <CheckCircle2 className="h-5 w-5 text-green-500" /> : <Circle className="h-5 w-5" />}
              </button>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className={`font-medium truncate ${t.status === 'completed' ? 'text-slate-400 line-through' : 'text-slate-900'}`}>{t.title}</h3>
                  <Badge>{t.status}</Badge>
                </div>
                {t.description && <p className="mt-1 text-sm text-slate-500 line-clamp-2">{t.description}</p>}
                {t.due_date && <p className="mt-1 text-xs text-slate-400">تاريخ الاستحقاق: {new Date(t.due_date).toLocaleDateString('ar-SA')}</p>}
              </div>
              <div className="flex gap-1 shrink-0">
                <button onClick={() => openEdit(t)} className="rounded-lg px-2 py-1 text-xs text-slate-500 hover:bg-gray-100 hover:text-slate-700 transition-colors">تعديل</button>
                <button onClick={() => handleDelete(t.id)} className="rounded-lg px-2 py-1 text-xs text-red-500 hover:bg-red-50 transition-colors">حذف</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {modalOpen && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content animate-scale-in" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editing ? 'تعديل مهمة' : 'إضافة مهمة'}</h2>
              <button type="button" onClick={closeModal} className="rounded-lg p-1.5 text-slate-400 hover:bg-gray-100 hover:text-slate-600"><X className="h-5 w-5" /></button>
            </div>
            <div className="space-y-4 p-6">
              <Input label="العنوان" required value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} />
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-700">الوصف</label>
                <textarea value={form.description} onChange={e => setForm({ ...form, description: e.target.value })}
                  className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-slate-900 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20" rows={3} />
              </div>
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-700">الحالة</label>
                <select value={form.status} onChange={e => setForm({ ...form, status: e.target.value })}
                  className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-slate-900 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20">
                  {Object.entries(statusLabels).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
                </select>
              </div>
            </div>
            <div className="flex justify-end gap-3 border-t border-gray-100 px-6 py-4">
              <Button variant="outline" onClick={closeModal}>إلغاء</Button>
              <Button onClick={handleSubmit} disabled={!form.title.trim() || saving}>
                {saving ? 'جاري الحفظ...' : editing ? 'حفظ التغييرات' : 'إضافة'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
