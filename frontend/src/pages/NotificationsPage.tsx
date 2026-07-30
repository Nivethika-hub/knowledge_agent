import { useCallback, useEffect, useState } from 'react'
import { Bell, CheckCircle2 } from 'lucide-react'

import { ErrorCard, LoadingCards } from '@/components/AsyncState'
import { SourceBadge } from '@/components/SourceBadge'
import { getApiErrorMessage } from '@/services/client'
import { getNotifications } from '@/services/notifications'
import type { Notification } from '@/types/api'

const formatDate = (date: string) => date ? new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(date)) : 'No timestamp'

export function NotificationsPage() {
  const [items, setItems] = useState<Notification[] | null>(null); const [error, setError] = useState<string | null>(null)
  const load = useCallback(async () => { setError(null); try { setItems(await getNotifications()) } catch (caught) { setError(getApiErrorMessage(caught)) } }, [])
  useEffect(() => { void load() }, [load])
  if (error) return <ErrorCard message={error} onRetry={() => void load()} />
  if (!items) return <LoadingCards count={4} />
  return <section className="mx-auto max-w-4xl overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"><div className="flex items-center justify-between border-b border-slate-100 p-6"><div><h2 className="font-bold text-slate-950">Knowledge updates</h2><p className="mt-1 text-sm text-slate-500">Results from automated refreshes and source events.</p></div><Bell className="size-5 text-slate-400" /></div>{items.length ? <div className="divide-y divide-slate-100">{items.map((item) => <article className="flex gap-4 p-5" key={item.notification_id}><div className="grid size-10 shrink-0 place-items-center rounded-xl bg-emerald-50 text-emerald-600"><CheckCircle2 className="size-5" /></div><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center gap-2"><p className="font-semibold text-slate-800">{item.feature_name}</p><SourceBadge source={item.event_source} /></div><p className="mt-2 text-sm text-slate-600">{item.message}</p><p className="mt-2 text-xs text-slate-400">{item.event_type} · {formatDate(item.created_at)}</p></div></article>)}</div> : <div className="p-12 text-center text-sm text-slate-500">No notifications yet.</div>}</section>
}
