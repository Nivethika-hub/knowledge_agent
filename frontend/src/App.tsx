import { Navigate, Route, Routes } from 'react-router-dom'

import { AppLayout } from '@/layouts/AppLayout'
import { AskAiPage } from '@/pages/AskAiPage'
import { AutomationPage } from '@/pages/AutomationPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { KnowledgeNodesPage } from '@/pages/KnowledgeNodesPage'
import { NotificationsPage } from '@/pages/NotificationsPage'
import { TimelinePage } from '@/pages/TimelinePage'

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="ask-ai" element={<AskAiPage />} />
        <Route path="knowledge-nodes" element={<KnowledgeNodesPage />} />
        <Route path="timeline" element={<TimelinePage />} />
        <Route path="notifications" element={<NotificationsPage />} />
        <Route path="automation" element={<AutomationPage />} />
      </Route>
      <Route path="*" element={<Navigate replace to="/" />} />
    </Routes>
  )
}
