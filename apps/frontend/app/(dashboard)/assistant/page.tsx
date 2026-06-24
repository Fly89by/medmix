'use client'

import { useState, useRef, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { api } from '@/lib/api'
import { Bot, Send, Loader2, User } from 'lucide-react'

interface ChatMessage { role: 'user' | 'assistant'; content: string }

export default function AssistantPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'assistant', content: 'مرحباً بك في MED.MIX OS! أنا المساعد الذكي. كيف يمكنني مساعدتك اليوم؟' },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [suggestions, setSuggestions] = useState<string[]>([])
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const handleSend = async (msg?: string) => {
    const text = (msg || input).trim()
    if (!text || loading) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: text }])
    setLoading(true)
    try {
      const res = await api.post<{ reply: string; suggestions: string[] }>('/assistant/chat', { message: text })
      setMessages(prev => [...prev, { role: 'assistant', content: res.reply }])
      setSuggestions(res.suggestions || [])
    } catch { setMessages(prev => [...prev, { role: 'assistant', content: 'عذراً، حدث خطأ. الرجاء المحاولة مرة أخرى.' }]) } finally { setLoading(false) }
  }

  return (
    <div className="space-y-6">
      <div className="page-header">
        <h1>المساعد الذكي</h1>
        <p>استفسر واحصل على إجابات من مساعد المبيعات الذكي</p>
      </div>
      <Card className="mx-auto max-w-3xl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10"><Bot className="h-4 w-4 text-primary" /></div>
            محادثة
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4 h-[400px] space-y-4 overflow-y-auto rounded-2xl bg-slate-50 p-4">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-start' : 'justify-end'} animate-fade-in`}>
                <div className={`flex max-w-[80%] items-start gap-2 rounded-2xl px-4 py-3 ${m.role === 'user' ? 'bg-primary text-white' : 'bg-white text-slate-900 shadow-sm border border-gray-100'}`}>
                  {m.role === 'assistant' && <Bot className="mt-1 h-4 w-4 shrink-0 opacity-60" />}
                  {m.role === 'user' && <User className="mt-1 h-4 w-4 shrink-0 opacity-60" />}
                  <p className="text-sm whitespace-pre-wrap leading-relaxed">{m.content}</p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-end animate-fade-in">
                <div className="flex items-center gap-2 rounded-2xl bg-white px-4 py-3 shadow-sm border border-gray-100">
                  <Loader2 className="h-4 w-4 animate-spin text-primary" />
                  <span className="text-sm text-slate-500">يكتب...</span>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {suggestions.length > 0 && (
            <div className="mb-4 flex flex-wrap gap-2">
              {suggestions.map((s, i) => (
                <button key={i} onClick={() => handleSend(s)}
                  className="rounded-full border border-gray-200 bg-white px-3 py-1.5 text-xs text-slate-600 hover:border-primary hover:text-primary hover:bg-primary/5 transition-colors">
                  {s}
                </button>
              ))}
            </div>
          )}

          <form onSubmit={e => { e.preventDefault(); handleSend() }} className="flex gap-2">
            <Input placeholder="اكتب رسالتك..." value={input} onChange={e => setInput(e.target.value)} className="flex-1" />
            <Button type="submit" disabled={!input.trim() || loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
