import { useCallback, useEffect, useState } from 'react'
import { Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { BookOpen, FolderKanban, GitBranch, MessageSquare, Ticket, Users } from 'lucide-react'

import { ErrorCard, LoadingCards } from '@/components/AsyncState'
import { StatCard } from '@/components/StatCard'
import { getApiErrorMessage } from '@/services/client'
import { getDashboardData, type DashboardData } from '@/services/dashboard'

const formatDate = (value?: string | null) => value ? new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value)) : 'No timestamp'

export function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setError(null)
    try { setData(await getDashboardData()) } catch (caught) { setError(getApiErrorMessage(caught)) }
  }, [])

  useEffect(() => { void load() }, [load])

  if (error) return <ErrorCard message={error} onRetry={() => void load()} />
  if (!data) return <LoadingCards count={6} />

  const stats = [
    { label: 'Projects', value: data.projects.length, icon: FolderKanban, tone: 'blue' as const },
    { label: 'Team Members', value: data.teamMembers.length, icon: Users, tone: 'violet' as const },
    { label: 'Slack Messages', value: data.slackMessages.length, icon: MessageSquare, tone: 'emerald' as const },
    { label: 'Jira Tickets', value: data.jiraTickets.length, icon: Ticket, tone: 'amber' as const },
    { label: 'GitHub Events', value: data.githubEvents.length, icon: GitBranch, tone: 'blue' as const },
    { label: 'Knowledge Nodes', value: data.knowledgeNodes.length, icon: BookOpen, tone: 'violet' as const },
  ]
  const distribution = [
    { name: 'Slack', value: data.slackMessages.length }, { name: 'Jira', value: data.jiraTickets.length },
    { name: 'GitHub', value: data.githubEvents.length }, { name: 'Knowledge', value: data.knowledgeNodes.length },
  ]
  const colors = ['#2563eb', '#7c3aed', '#059669', '#f59e0b']
  const activities = data.githubEvents.slice(0, 5)

  return <div className="space-y-8">
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>
    <section className="grid gap-6 xl:grid-cols-5">
      <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm xl:col-span-3"><h2 className="text-lg font-bold text-slate-950">Knowledge activity</h2><p className="text-sm text-slate-500">Records currently available from each connected source.</p><div className="mt-6 h-72"><ResponsiveContainer width="100%" height="100%"><BarChart data={distribution}><XAxis dataKey="name" axisLine={false} tickLine={false} /><YAxis allowDecimals={false} axisLine={false} tickLine={false} /><Tooltip cursor={{ fill: '#f8fafc' }} /><Bar dataKey="value" radius={[7, 7, 0, 0]} fill="#2563eb" /></BarChart></ResponsiveContainer></div></article>
      <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm xl:col-span-2"><h2 className="text-lg font-bold text-slate-950">Source distribution</h2><div className="mt-5 h-48"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={distribution} dataKey="value" nameKey="name" innerRadius={48} outerRadius={75} paddingAngle={3}>{distribution.map((entry, index) => <Cell key={entry.name} fill={colors[index]} />)}</Pie><Tooltip /></PieChart></ResponsiveContainer></div><div className="grid grid-cols-2 gap-2 text-xs">{distribution.map((item, index) => <span className="flex items-center gap-2 text-slate-600" key={item.name}><i className="size-2 rounded-full" style={{ background: colors[index] }} />{item.name}: {item.value}</span>)}</div></article>
    </section>
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"><div className="flex items-center justify-between"><div><h2 className="text-lg font-bold text-slate-950">Recent GitHub activity</h2><p className="text-sm text-slate-500">Latest events received by the knowledge agent.</p></div><GitBranch className="size-5 text-slate-400" /></div><div className="mt-5 divide-y divide-slate-100">{activities.length ? activities.map((event, index) => <div className="flex gap-4 py-4" key={event.github_event_id ?? index}><div className="grid size-9 shrink-0 place-items-center rounded-xl bg-slate-100 text-slate-700"><GitBranch className="size-4" /></div><div className="min-w-0 flex-1"><p className="truncate text-sm font-semibold text-slate-800">{event.title ?? event.event_type ?? 'GitHub event'}</p><p className="mt-1 truncate text-sm text-slate-500">{event.related_feature ?? 'Uncategorized'}</p></div><time className="hidden text-xs text-slate-400 sm:block">{formatDate(event.event_time)}</time></div>) : <p className="py-8 text-center text-sm text-slate-500">No GitHub events returned by the backend.</p>}</div></section>
  </div>
}
