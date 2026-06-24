'use client';

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { getMe, logout, type User } from "@/lib/auth";
import {
  LayoutDashboard,
  Building2,
  Target,
  FileText,
  BarChart3,
  Bot,
  BookOpen,
  ListChecks,
  LogOut,
  Menu,
  X,
  ChevronLeft,
  Search,
  Bell,
  UserCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "لوحة التحكم", icon: LayoutDashboard },
  { href: "/crm", label: "إدارة العملاء", icon: Building2 },
  { href: "/leads", label: "العملاء المحتملين", icon: Target },
  { href: "/quotes", label: "عروض الأسعار", icon: FileText },
  { href: "/analytics", label: "التحليلات", icon: BarChart3 },
  { href: "/assistant", label: "المساعد الذكي", icon: Bot },
  { href: "/knowledge", label: "قاعدة المعرفة", icon: BookOpen },
  { href: "/tasks", label: "المهام", icon: ListChecks },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    getMe()
      .then(setUser)
      .catch(() => router.push("/login"));
  }, [router]);

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-gray-50 to-blue-50/30">
      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 right-0 z-50 flex w-72 flex-col bg-gradient-to-b from-slate-900 via-slate-900 to-slate-800 shadow-2xl transition-transform duration-300 lg:static lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "translate-x-full lg:translate-x-0",
        )}
      >
        {/* Logo */}
        <div className="flex h-16 items-center justify-between border-b border-white/10 px-6">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary-700 shadow-lg">
              <Bot className="h-5 w-5 text-white" />
            </div>
            <div>
              <span className="text-lg font-bold text-white">MED.MIX</span>
              <span className="mr-2 text-[10px] font-medium text-blue-300">OS</span>
            </div>
          </Link>
          <button
            className="rounded-lg p-1.5 text-white/50 hover:bg-white/10 hover:text-white lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 space-y-1 p-4">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setSidebarOpen(false)}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-primary/15 text-white shadow-sm"
                    : "text-slate-400 hover:bg-white/5 hover:text-white",
                )}
              >
                <span className={cn("flex h-8 w-8 items-center justify-center rounded-lg", isActive ? "bg-primary/20" : "")}>
                  <Icon className={cn("h-4 w-4", isActive ? "text-primary-400" : "")} />
                </span>
                {item.label}
                {isActive && <span className="mr-auto h-1.5 w-1.5 rounded-full bg-primary-400" />}
              </Link>
            );
          })}
        </nav>

        {/* User */}
        <div className="border-t border-white/10 p-4">
          {user && (
            <div className="mb-3 flex items-center gap-3 rounded-xl bg-white/5 px-3 py-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-primary to-purple-600 text-xs font-bold text-white shadow">
                {user.name.charAt(0)}
              </div>
              <div className="flex-1 truncate">
                <p className="text-sm font-medium text-white">{user.name}</p>
                <p className="text-xs text-slate-400">{user.email}</p>
              </div>
            </div>
          )}
          <button
            onClick={logout}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-400 transition-all duration-200 hover:bg-red-500/10 hover:text-red-400"
          >
            <LogOut className="h-4 w-4" />
            تسجيل الخروج
          </button>
        </div>
      </aside>

      {/* Overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Main Area */}
      <div className="flex min-h-screen flex-1 flex-col">
        {/* Header */}
        <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-gray-200/80 bg-white/80 backdrop-blur-xl px-4 lg:px-8">
          <button
            className="flex h-9 w-9 items-center justify-center rounded-xl text-slate-500 hover:bg-gray-100 hover:text-slate-700 lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </button>

          <div className="hidden lg:flex lg:flex-1" />

          <div className="flex items-center gap-3">
            <button className="relative flex h-9 w-9 items-center justify-center rounded-xl text-slate-400 hover:bg-gray-100 hover:text-slate-600 transition-colors">
              <Bell className="h-4 w-4" />
              <span className="absolute -top-0.5 -right-0.5 h-2 w-2 rounded-full bg-red-500 ring-2 ring-white" />
            </button>
            <button className="flex items-center gap-2 rounded-xl px-3 py-1.5 text-sm text-slate-600 hover:bg-gray-100 transition-colors">
              <UserCircle className="h-5 w-5" />
              <span className="hidden sm:inline">{user?.name || "..."}</span>
            </button>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 p-4 lg:p-8 animate-fade-in">
          {children}
        </main>
      </div>
    </div>
  );
}
