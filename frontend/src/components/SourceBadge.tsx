import { FileText, GitBranch, MessageSquare, Ticket } from 'lucide-react'

const sourceStyles: Record<string, { className: string; icon: typeof GitBranch }> = {
  Slack: { className: 'bg-fuchsia-50 text-fuchsia-700', icon: MessageSquare },
  Jira: { className: 'bg-blue-50 text-blue-700', icon: Ticket },
  GitHub: { className: 'bg-slate-100 text-slate-700', icon: GitBranch },
  Notion: { className: 'bg-stone-100 text-stone-700', icon: FileText },
}

export function SourceBadge({ source }: { source: string }) {
  const config = sourceStyles[source] ?? { className: 'bg-slate-100 text-slate-700', icon: FileText }
  const Icon = config.icon
  return <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${config.className}`}><Icon className="size-3.5" />{source}</span>
}
