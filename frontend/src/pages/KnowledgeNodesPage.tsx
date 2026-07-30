import { useCallback, useEffect, useState } from 'react'
import { BookOpen, ChevronDown, Users } from 'lucide-react'

import { ErrorCard, LoadingCards } from '@/components/AsyncState'
import { SourceBadge } from '@/components/SourceBadge'
import { getApiErrorMessage } from '@/services/client'
import { getKnowledgeNodes } from '@/services/knowledge'
import type { KnowledgeNode } from '@/types/api'

export function KnowledgeNodesPage() {
  const [nodes, setNodes] = useState<KnowledgeNode[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [expanded, setExpanded] = useState<string | null>(null)

  const load = useCallback(async () => {
    setError(null)
    try { setNodes(await getKnowledgeNodes()) } catch (caught) { setError(getApiErrorMessage(caught)) }
  }, [])

  useEffect(() => { void load() }, [load])
  if (error) return <ErrorCard message={error} onRetry={() => void load()} />
  if (!nodes) return <LoadingCards count={3} />
  if (!nodes.length) return <EmptyNodes />

  return <div className="space-y-4">
    <section className="rounded-2xl border border-blue-100 bg-blue-50/60 p-5 text-sm text-blue-900"><strong>{nodes.length} knowledge nodes</strong> synthesize the decisions, evidence, and participants from all connected sources.</section>
    {nodes.map((node) => {
      const isExpanded = expanded === node.feature_name
      const sources = [
        ['Slack', node.slack_messages.length], ['Jira', node.jira_tickets.length],
        ['GitHub', node.github_events.length], ['Notion', node.notion_documents.length],
      ].filter(([, count]) => count as number)
      return <article className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm" key={node.feature_name}>
        <button className="flex w-full items-start gap-4 p-5 text-left sm:p-6" onClick={() => setExpanded(isExpanded ? null : node.feature_name)} aria-expanded={isExpanded}>
          <div className="grid size-11 shrink-0 place-items-center rounded-xl bg-violet-50 text-violet-700"><BookOpen className="size-5" /></div>
          <div className="min-w-0 flex-1"><h2 className="text-base font-bold text-slate-950">{node.feature_name}</h2><p className="mt-1 line-clamp-2 text-sm leading-6 text-slate-600">{node.decision || 'No decision summary available.'}</p><div className="mt-3 flex flex-wrap gap-2">{sources.map(([source]) => <SourceBadge key={source as string} source={source as string} />)}</div></div>
          <ChevronDown className={`mt-2 size-5 shrink-0 text-slate-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
        </button>
        {isExpanded && <div className="grid gap-6 border-t border-slate-100 p-5 sm:grid-cols-2 sm:p-6"><section><h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Why this decision</h3><p className="mt-2 text-sm leading-6 text-slate-700">{node.reason || 'No rationale available.'}</p><h3 className="mt-6 flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-500"><Users className="size-3.5" /> Participants</h3><div className="mt-3 flex flex-wrap gap-2">{node.participants.length ? node.participants.map((person) => <span className="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-700" key={person.member_id}>{person.full_name}{person.role ? ` · ${person.role}` : ''}</span>) : <span className="text-sm text-slate-500">No participants listed.</span>}</div></section><section><h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Evidence timeline</h3><div className="mt-3 space-y-3">{node.timeline.slice(0, 5).map((item, index) => <div className="border-l-2 border-blue-100 pl-3" key={`${item.timestamp}-${index}`}><p className="text-sm font-medium text-slate-700">{item.title}</p><p className="mt-0.5 text-xs text-slate-500">{item.platform} · {item.timestamp}</p></div>)}</div></section></div>}
      </article>
    })}
  </div>
}

function EmptyNodes() { return <section className="rounded-2xl border border-dashed border-slate-300 bg-white p-12 text-center"><BookOpen className="mx-auto size-8 text-slate-400" /><h2 className="mt-4 font-bold text-slate-900">No knowledge nodes yet</h2><p className="mt-2 text-sm text-slate-500">Add source data, then refresh the knowledge index.</p></section> }
