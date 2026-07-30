import { useState } from 'react'
import { ArrowUp, BrainCircuit, ChevronDown, Clock3, Sparkles } from 'lucide-react'

import { SourceBadge } from '@/components/SourceBadge'
import { getApiErrorMessage } from '@/services/client'
import { askAgent } from '@/services/agent'
import type { AgentAnswer } from '@/types/api'

const example = 'Why did the team choose PostgreSQL?'

export function AskAiPage() {
  const [question, setQuestion] = useState(example)
  const [answer, setAnswer] = useState<AgentAnswer | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  async function submit() {
    if (!question.trim() || isLoading) return
    setIsLoading(true); setError(null)
    try { setAnswer(await askAgent(question.trim())) } catch (caught) { setError(getApiErrorMessage(caught)) } finally { setIsLoading(false) }
  }

  return <div className="mx-auto max-w-5xl space-y-8">
    <section className="overflow-hidden rounded-3xl bg-gradient-to-br from-blue-700 via-blue-600 to-indigo-700 p-7 text-white shadow-xl shadow-blue-100 sm:p-10"><div className="max-w-2xl"><span className="inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1 text-xs font-semibold"><Sparkles className="size-3.5" /> Evidence-backed intelligence</span><h2 className="mt-5 text-3xl font-bold tracking-tight sm:text-4xl">Ask anything about your organization.</h2><p className="mt-3 text-blue-100">Trace decisions, people, and events across your connected knowledge sources.</p></div><div className="mt-8 rounded-2xl bg-white p-2 shadow-2xl"><textarea className="min-h-28 w-full resize-none rounded-xl border-0 p-4 text-base text-slate-800 outline-none placeholder:text-slate-400" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask anything about your organization..." onKeyDown={(event) => { if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') void submit() }} /><div className="flex items-center justify-between px-2 pb-1"><span className="text-xs text-slate-400">⌘ / Ctrl + Enter to submit</span><button onClick={() => void submit()} disabled={isLoading || !question.trim()} className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60">{isLoading ? <><span className="size-4 animate-spin rounded-full border-2 border-white border-t-transparent" />Thinking…</> : <>Ask AI <ArrowUp className="size-4" /></>}</button></div></div></section>
    {error && <div className="rounded-2xl border border-rose-200 bg-rose-50 p-5 text-sm text-rose-800">{error}</div>}
    {isLoading && <section className="animate-pulse rounded-2xl border border-slate-200 bg-white p-7 shadow-sm"><div className="h-5 w-48 rounded bg-slate-200" /><div className="mt-5 h-4 w-full rounded bg-slate-100" /><div className="mt-3 h-4 w-5/6 rounded bg-slate-100" /><div className="mt-3 h-4 w-3/4 rounded bg-slate-100" /></section>}
    {answer && !isLoading && <section className="space-y-6"><article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8"><div className="flex flex-wrap items-center justify-between gap-3"><div className="flex items-center gap-3"><div className="grid size-10 place-items-center rounded-xl bg-blue-50 text-blue-600"><BrainCircuit className="size-5" /></div><div><h2 className="font-bold text-slate-950">AI Answer</h2><p className="text-sm text-slate-500">Synthesized from retrieved organizational evidence</p></div></div><span className="rounded-full bg-blue-50 px-3 py-1.5 text-sm font-bold text-blue-700">{Math.round(answer.confidence * 100)}% confidence</span></div><div className="mt-7 whitespace-pre-wrap leading-7 text-slate-700">{answer.answer}</div></article>
      <div className="grid gap-6 lg:grid-cols-2"><article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"><h3 className="font-bold text-slate-950">Timeline</h3><div className="mt-5 space-y-4">{answer.timeline.map((item, index) => <div className="flex gap-3" key={`${item.timestamp}-${index}`}><div className="mt-1.5 size-2 shrink-0 rounded-full bg-blue-500 ring-4 ring-blue-50" /><div><p className="text-sm font-semibold text-slate-700">{item.title}</p><p className="mt-1 text-xs text-slate-500"><Clock3 className="mr-1 inline size-3" />{item.timestamp} · {item.feature}</p></div></div>)}</div></article><article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"><h3 className="font-bold text-slate-950">Citations</h3><div className="mt-5 space-y-4">{answer.citations.map((citation, index) => <div className="rounded-xl bg-slate-50 p-3" key={`${citation.reference}-${index}`}><SourceBadge source={citation.source} /><p className="mt-2 text-sm text-slate-700">{citation.reference}</p>{citation.timestamp && <p className="mt-1 text-xs text-slate-400">{citation.timestamp}</p>}</div>)}</div></article></div>
      {answer.errors.length > 0 && <details className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800"><summary className="cursor-pointer font-semibold">Answer processing note</summary><p className="mt-2">{answer.errors.join(' ')}</p><ChevronDown className="hidden" /></details>}
    </section>}
  </div>
}
