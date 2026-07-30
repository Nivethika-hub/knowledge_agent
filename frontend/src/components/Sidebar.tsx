import {
  Bell,
  BookOpen,
  Bot,
  Gauge,
  Home,
  Menu,
  Settings2,
  X,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'

const navigationItems = [
  { label: 'Dashboard', to: '/', icon: Home, end: true },
  { label: 'Ask AI', to: '/ask-ai', icon: Bot },
  { label: 'Knowledge Nodes', to: '/knowledge-nodes', icon: BookOpen },
  { label: 'Timeline', to: '/timeline', icon: Gauge },
  { label: 'Notifications', to: '/notifications', icon: Bell },
  { label: 'Automation', to: '/automation', icon: Settings2 },
]

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
  onOpen: () => void
}

export function Sidebar({ isOpen, onClose, onOpen }: SidebarProps) {
  return (
    <>
      <button
        aria-label="Open navigation"
        className="fixed left-4 top-4 z-30 rounded-xl border border-slate-200 bg-white p-2.5 text-slate-700 shadow-sm lg:hidden"
        onClick={onOpen}
      >
        <Menu className="size-5" />
      </button>

      {isOpen && (
        <button
          aria-label="Close navigation overlay"
          className="fixed inset-0 z-30 bg-slate-950/30 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-72 flex-col border-r border-slate-200 bg-white px-4 py-6 shadow-xl transition-transform duration-300 lg:translate-x-0 lg:shadow-none ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="mb-10 flex items-center justify-between px-2">
          <div className="flex items-center gap-3">
            <div className="grid size-10 place-items-center rounded-xl bg-blue-600 text-white shadow-lg shadow-blue-200">
              <Bot className="size-5" />
            </div>
            <div>
              <p className="text-sm font-bold tracking-tight text-slate-900">Knowledge Agent</p>
              <p className="text-xs text-slate-500">Context intelligence</p>
            </div>
          </div>
          <button
            aria-label="Close navigation"
            className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 lg:hidden"
            onClick={onClose}
          >
            <X className="size-5" />
          </button>
        </div>

        <nav className="space-y-1" aria-label="Main navigation">
          {navigationItems.map(({ label, to, icon: Icon, end }) => (
            <NavLink
              end={end}
              key={to}
              onClick={onClose}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-950'
                }`
              }
            >
              <Icon className="size-5" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="mt-auto rounded-2xl bg-slate-50 p-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">System status</p>
          <div className="mt-3 flex items-center gap-2 text-sm font-medium text-emerald-700">
            <span className="size-2 rounded-full bg-emerald-500" />
            Backend connected
          </div>
        </div>
      </aside>
    </>
  )
}
