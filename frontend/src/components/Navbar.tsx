import { Bell, Search } from 'lucide-react'
import { useLocation } from 'react-router-dom'

const pageTitles: Record<string, { title: string; subtitle: string }> = {
  '/': { title: 'Dashboard', subtitle: 'Your organization knowledge at a glance' },
  '/ask-ai': { title: 'Ask AI', subtitle: 'Explore decisions with evidence-backed answers' },
  '/knowledge-nodes': { title: 'Knowledge Nodes', subtitle: 'Structured context across your organization' },
  '/timeline': { title: 'Timeline', subtitle: 'Follow events across every connected source' },
  '/notifications': { title: 'Notifications', subtitle: 'Automation and knowledge refresh activity' },
  '/automation': { title: 'Automation', subtitle: 'Keep your knowledge graph current' },
}

export function Navbar() {
  const { pathname } = useLocation()
  const page = pageTitles[pathname] ?? pageTitles['/']

  return (
    <header className="flex min-h-20 items-center justify-between gap-4 border-b border-slate-200 bg-white px-5 py-4 lg:px-8">
      <div className="ml-12 min-w-0 lg:ml-0">
        <h1 className="truncate text-xl font-bold tracking-tight text-slate-950 lg:text-2xl">{page.title}</h1>
        <p className="mt-0.5 truncate text-sm text-slate-500">{page.subtitle}</p>
      </div>

      <div className="flex items-center gap-2 sm:gap-4">
        <button
          aria-label="Search"
          className="hidden rounded-xl border border-slate-200 p-2.5 text-slate-500 transition-colors hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 sm:inline-flex"
        >
          <Search className="size-5" />
        </button>
        <button
          aria-label="Notifications"
          className="relative rounded-xl border border-slate-200 p-2.5 text-slate-500 transition-colors hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
        >
          <Bell className="size-5" />
          <span className="absolute right-2 top-2 size-2 rounded-full border-2 border-white bg-blue-600" />
        </button>
        <div className="hidden items-center gap-3 border-l border-slate-200 pl-4 sm:flex">
          <div className="grid size-9 place-items-center rounded-full bg-blue-100 text-sm font-bold text-blue-700">NA</div>
          <div className="hidden xl:block">
            <p className="text-sm font-semibold text-slate-800">Knowledge Admin</p>
            <p className="text-xs text-slate-500">Workspace owner</p>
          </div>
        </div>
      </div>
    </header>
  )
}
