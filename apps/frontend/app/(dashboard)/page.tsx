'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Building2, Users, Target, FileText, TrendingUp, TrendingDown, Activity, Clock, ArrowLeft, Sparkles, UserPlus, DollarSign } from "lucide-react";
import { api } from '@/lib/api';
import { getMe, type User } from '@/lib/auth';

interface DashboardData {
  companies_total: number;
  contacts_total: number;
  projects_total: number;
  leads_total: number;
  active_leads: number;
  quotes_this_month: number;
  leads_by_status: Record<string, number>;
  recent_activities: { id: number; action: string; entity_type: string; description: string; created_at: string }[];
}

const statusLabels: Record<string, string> = {
  NEW: 'جديد',
  QUALIFIED: 'مؤهل',
  CONTACTED: 'تم الاتصال',
  NEGOTIATING: 'قيد التفاوض',
  WON: 'تم البيع',
  LOST: 'ملغي',
};

const statusColors: Record<string, string> = {
  NEW: 'bg-blue-500',
  QUALIFIED: 'bg-purple-500',
  CONTACTED: 'bg-amber-500',
  NEGOTIATING: 'bg-orange-500',
  WON: 'bg-emerald-500',
  LOST: 'bg-red-500',
};

const formatTime = (dateStr: string) => {
  const d = new Date(dateStr);
  const diff = Math.floor((Date.now() - d.getTime()) / 60000);
  if (diff < 1) return 'الآن';
  if (diff < 60) return `منذ ${diff} دقيقة`;
  if (diff < 1440) return `منذ ${Math.floor(diff / 60)} ساعة`;
  return d.toLocaleDateString('ar-SA');
};

const maxLeadsForWidth = (obj: Record<string, number>) => Math.max(...Object.values(obj), 1);

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    getMe().then(setUser).catch(() => {});
    api.get<DashboardData>('/dashboard')
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="page-header">
          <div className="skeleton h-8 w-48" />
          <div className="skeleton mt-2 h-4 w-72" />
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[1,2,3,4].map(i => <div key={i} className="stat-card"><div className="skeleton h-20 w-full" /></div>)}
        </div>
        <div className="content-card p-6"><div className="skeleton h-48 w-full" /></div>
      </div>
    );
  }

  const maxVal = data?.leads_by_status ? maxLeadsForWidth(data.leads_by_status) : 1;

  const stats = [
    {
      title: 'إجمالي الشركات', value: String(data?.companies_total ?? 0),
      sub: `${data?.companies_total || 0} شركة مسجلة`,
      icon: Building2, change: '+12%', trend: 'up',
      gradient: 'from-blue-600 to-blue-500', bg: 'bg-blue-50',
    },
    {
      title: 'جهات الاتصال', value: String(data?.contacts_total ?? 0),
      sub: `${data?.contacts_total || 0} جهة اتصال`,
      icon: Users, change: '+8%', trend: 'up',
      gradient: 'from-emerald-600 to-emerald-500', bg: 'bg-emerald-50',
    },
    {
      title: 'العملاء المحتملين', value: String(data?.active_leads ?? 0),
      sub: `من أصل ${data?.leads_total || 0} عميل محتمل`,
      icon: Target, change: `${data?.active_leads || 0} نشط`, trend: data?.active_leads ? 'up' : 'down',
      gradient: 'from-purple-600 to-purple-500', bg: 'bg-purple-50',
    },
    {
      title: 'عروض الأسعار هذا الشهر', value: String(data?.quotes_this_month ?? 0),
      sub: 'عرض سعر خلال 30 يوم',
      icon: FileText, change: 'هذا الشهر', trend: 'up',
      gradient: 'from-orange-600 to-orange-500', bg: 'bg-orange-50',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            مرحباً{user ? `، ${user.name}` : ''} 👋
          </h1>
          <p className="mt-1 text-sm text-slate-500">نظرة عامة على أداء المبيعات ونشاط النظام</p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.title} className="stat-card group">
              <div className="flex items-start gap-4">
                <div className={`icon-wrapper ${stat.bg}`}>
                  <Icon className={`h-6 w-6 ${stat.trend === 'up' ? 'text-blue-600' : 'text-orange-600'}`} />
                </div>
                <div className="flex-1">
                  <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{stat.title}</p>
                  <div className="mt-1 flex items-baseline gap-2">
                    <p className="text-3xl font-bold text-slate-900">{stat.value}</p>
                    <span className={`flex items-center gap-0.5 text-xs font-medium ${stat.trend === 'up' ? 'text-emerald-600' : 'text-red-500'}`}>
                      {stat.trend === 'up' ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                      {stat.change}
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-slate-400">{stat.sub}</p>
                </div>
              </div>
              <div className={`absolute left-0 top-0 h-1 w-full bg-gradient-to-r ${stat.gradient} opacity-0 transition-opacity group-hover:opacity-100`} />
            </div>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Leads by Status */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-primary" />
              توزيع العملاء المحتملين
            </CardTitle>
          </CardHeader>
          <CardContent>
            {data?.leads_by_status && Object.keys(data.leads_by_status).length > 0 ? (
              <div className="space-y-4">
                {Object.entries(data.leads_by_status).map(([status, count]) => {
                  const pct = (count as number / maxVal) * 100;
                  return (
                    <div key={status} className="group">
                      <div className="mb-1.5 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className={`h-2.5 w-2.5 rounded-full ${statusColors[status] || 'bg-gray-400'}`} />
                          <span className="text-sm font-medium text-slate-700">{statusLabels[status] || status}</span>
                        </div>
                        <span className="text-sm font-bold text-slate-900">{count as number}</span>
                      </div>
                      <div className="h-2 overflow-hidden rounded-full bg-gray-100">
                        <div
                          className={`h-full rounded-full ${statusColors[status] || 'bg-gray-400'} transition-all duration-500`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="empty-state">
                <Target className="empty-state-icon" />
                <h3>لا يوجد عملاء محتملين</h3>
                <p>قم بإضافة عميل محتمل جديد لبدء التتبع</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-primary" />
              آخر النشاطات
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {(data?.recent_activities ?? []).length === 0 ? (
              <div className="empty-state px-6">
                <Clock className="empty-state-icon" />
                <h3>لا توجد نشاطات</h3>
                <p>سيتم تسجيل النشاطات هنا تلقائياً</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-50">
                {data?.recent_activities.slice(0, 6).map((activity, i) => (
                  <div key={activity.id} className="flex items-start gap-3 px-5 py-3.5 transition-colors hover:bg-gray-50/50 animate-fade-in" style={{ animationDelay: `${i * 50}ms` }}>
                    <div className="mt-0.5 flex h-7 w-7 items-center justify-center rounded-full bg-primary/10">
                      <Activity className="h-3.5 w-3.5 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-slate-700 truncate">{activity.description}</p>
                      <p className="mt-0.5 text-xs text-slate-400">{formatTime(activity.created_at)}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            إجراءات سريعة
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { label: 'إضافة شركة', icon: Building2, href: '/crm', color: 'text-blue-600', bg: 'bg-blue-50' },
              { label: 'عميل محتمل جديد', icon: UserPlus, href: '/leads', color: 'text-purple-600', bg: 'bg-purple-50' },
              { label: 'عرض سعر جديد', icon: DollarSign, href: '/quotes', color: 'text-orange-600', bg: 'bg-orange-50' },
              { label: 'عرض التحليلات', icon: TrendingUp, href: '/analytics', color: 'text-emerald-600', bg: 'bg-emerald-50' },
            ].map((action) => {
              const Icon = action.icon;
              return (
                <a
                  key={action.label}
                  href={action.href}
                  className="flex items-center gap-3 rounded-xl border border-gray-100 p-4 transition-all duration-200 hover:shadow-md hover:-translate-y-0.5 group"
                >
                  <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${action.bg} ${action.color}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-slate-700">{action.label}</p>
                  </div>
                  <ArrowLeft className="h-4 w-4 text-slate-300 transition-transform group-hover:-translate-x-1" />
                </a>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
