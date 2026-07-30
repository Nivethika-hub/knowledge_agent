import { useCallback, useEffect, useMemo, useState } from 'react'
import { Clock3, Filter } from 'lucide-react'

import { ErrorCard, LoadingCards } from '@/components/AsyncState'
import { SourceBadge } from '@/components/SourceBadge'
import { getApiErrorMessage } from '@/services/client'
import { getTimeline } from '@/services/timeline'
import type { TimelineItem } from '@/types/api'

const formatDate = (date: string) => date ? new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(date)) : 'No timestamp'

export function TimelinePage() {
  const [events, setEvents] = useState<TimelineItem[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [source, setSource] = useState('All')
  const load = useCallback(async () => { setError(null); try { setEvents(await getTimeline()) } catch (caught) { setError(getApiErrorMessage(caught)) } }, [])
  useEffect(() => { void load() }, [load])
  const sources = useMemo(() => ['All', ...new Set(events?.map((event) => event.platform) ?? [])], [events])
  const filtered = source === 'All' ? events : events?.filter((event) => event.platform === source)
  if (error) return <ErrorCard message={error} onRetry={() => void load()} />
  if (!events) return <LoadingCards count={5} />
  return <div className="mx-auto max-w-5xl"><section className="mb-6 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"><div className="flex items-center gap-2 text-sm font-medium text-slate-600"><Filter className="size-4" /> Filter source</div><div className="flex flex-wrap gap-2">{sources.map((item) => <button key={item} onClick={() => setSource(item)} className={`rounded-full px-3 py-1.5 text-sm font-medium transition ${source === item ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}>{item}</button>)}</div></section><section className="relative space-y-1 before:absolute before:bottom-3 before:left-5 before:top-3 before:w-px before:bg-slate-200">{filtered?.length ? filtered.map((event, index) => <article className="relative flex gap-4 py-3" key={`${event.timestamp}-${event.platform}-${index}`}><div className="z-10 grid size-10 shrink-0 place-items-center rounded-full bg-white text-blue-600 ring-1 ring-slate-200"><Clock3 className="size-4" /></div><div className="min-w-0 flex-1 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"><div className="flex flex-wrap items-center justify-between gap-2"><SourceBadge source={event.platform} /><time className="text-xs text-slate-400">{formatDate(event.timestamp)}</time></div><h2 className="mt-3 font-semibold text-slate-900">{event.title}</h2><p className="mt-1 text-sm text-slate-500">{event.feature}</p></div></article>) : <p className="py-12 text-center text-sm text-slate-500">No events match this source filter.</p>}</section></div>
}
