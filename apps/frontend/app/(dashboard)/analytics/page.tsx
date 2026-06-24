'use client'

import { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { api } from '@/lib/api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

interface AnalyticsData {
  quotes_trend: { year: number; month: number; count: number }[]
  leads_by_status: Record<string, number>
  leads_by_source: Record<string, number>
}

const COLORS = ['#2563eb', '#16a34a', '#9333ea', '#d97706', '#dc2626', '#64748b']
const statusLabels: Record<string, string> = { NEW: 'جديد', QUALIFIED: 'مؤهل', CONTACTED: 'تم الاتصال', NEGOTIATING: 'قيد التفاوض', WON: 'تم البيع', LOST: 'ملغي' }
const sourceLabels: Record<string, string> = { website: 'موقع إلكتروني', referral: 'إحالة', social_media: 'تواصل اجتماعي', cold_call: 'اتصال بارد', manual: 'يدوي', other: 'آخر' }
const monthNames = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get<AnalyticsData>('/analytics/overview')
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="space-y-6">
      <div className="page-header"><h1>التحليلات</h1><p>إحصائيات ومؤشرات أداء المبيعات</p></div>
      <div className="flex justify-center py-20"><div className="skeleton h-8 w-48" /></div>
    </div>
  )

  const trendData = data?.quotes_trend?.map(d => ({ name: monthNames[d.month - 1], count: d.count })) || []
  const statusData = Object.entries(data?.leads_by_status || {}).map(([k, v]) => ({ name: statusLabels[k] || k, value: v as number }))
  const sourceData = Object.entries(data?.leads_by_source || {}).map(([k, v]) => ({ name: sourceLabels[k] || k, value: v as number }))

  return (
    <div className="space-y-6">
      <div className="page-header">
        <h1>التحليلات</h1>
        <p>إحصائيات ومؤشرات أداء المبيعات</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>عروض الأسعار (آخر 6 أشهر)</CardTitle></CardHeader>
          <CardContent>
            {trendData.length === 0 ? (
              <div className="flex items-center justify-center h-[300px] text-slate-400 text-sm">لا توجد بيانات كافية</div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={trendData}>
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0' }} />
                  <Bar dataKey="count" fill="#2563eb" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>العملاء المتوقعون حسب الحالة</CardTitle></CardHeader>
          <CardContent>
            {statusData.length === 0 ? (
              <div className="flex items-center justify-center h-[300px] text-slate-400 text-sm">لا توجد بيانات كافية</div>
            ) : (
              <>
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie data={statusData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                      {statusData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex flex-wrap gap-3 mt-2">
                  {statusData.map((d, i) => (
                    <div key={d.name} className="flex items-center gap-2 text-sm">
                      <div className="h-3 w-3 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                      <span className="text-slate-600">{d.name}: {d.value}</span>
                    </div>
                  ))}
                </div>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>العملاء المتوقعون حسب المصدر</CardTitle></CardHeader>
          <CardContent>
            {sourceData.length === 0 ? (
              <div className="flex items-center justify-center h-[300px] text-slate-400 text-sm">لا توجد بيانات كافية</div>
            ) : (
              <>
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie data={sourceData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                      {sourceData.map((_, i) => <Cell key={i} fill={COLORS[(i + 2) % COLORS.length]} />)}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex flex-wrap gap-3 mt-2">
                  {sourceData.map((d, i) => (
                    <div key={d.name} className="flex items-center gap-2 text-sm">
                      <div className="h-3 w-3 rounded-full" style={{ backgroundColor: COLORS[(i + 2) % COLORS.length] }} />
                      <span className="text-slate-600">{d.name}: {d.value}</span>
                    </div>
                  ))}
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
