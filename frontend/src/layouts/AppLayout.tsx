import { useState } from 'react'
import { Outlet } from 'react-router-dom'

import { Navbar } from '@/components/Navbar'
import { Sidebar } from '@/components/Sidebar'

export function AppLayout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-slate-50">
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        onOpen={() => setIsSidebarOpen(true)}
      />
      <div className="min-h-screen lg:pl-72">
        <Navbar />
        <main className="mx-auto w-full max-w-screen-2xl p-5 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
