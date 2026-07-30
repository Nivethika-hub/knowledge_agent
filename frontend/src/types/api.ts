export interface Project {
  project_id: number
  project_name: string
  company_name?: string | null
  description?: string | null
  status?: string | null
  start_date?: string | null
  created_at?: string | null
}

export interface TeamMember {
  member_id: number
  project_id: number
  full_name: string
  role?: string | null
  email?: string | null
}

export interface SourceEvent {
  message_id?: number
  jira_id?: number
  github_event_id?: number
  document_id?: number
  project_id: number
  related_feature?: string | null
  title?: string | null
  description?: string | null
  message?: string | null
  event_type?: string | null
  event_time?: string | null
  message_time?: string | null
  created_at?: string | null
  updated_at?: string | null
}

export interface Participant {
  member_id: number
  full_name: string
  role?: string | null
}

export interface TimelineItem {
  timestamp: string
  platform: 'Slack' | 'Jira' | 'GitHub' | 'Notion' | string
  title: string
  feature: string
}

export interface KnowledgeNode {
  feature_name: string
  decision: string
  reason: string
  participants: Participant[]
  timeline: TimelineItem[]
  slack_messages: string[]
  jira_tickets: string[]
  github_events: string[]
  notion_documents: string[]
  generated_at: string
}

export interface Citation {
  source: 'Slack' | 'Jira' | 'GitHub' | 'Notion' | string
  reference: string
  timestamp?: string
  feature?: string
}

export interface AgentAnswer {
  answer: string
  confidence: number
  timeline: TimelineItem[]
  citations: Citation[]
  errors: string[]
}

export interface AutomationResult {
  events_detected: number
  updated_features: string[]
  vectors_updated: number
  notifications_created: number
  status: string
}

export interface Notification {
  notification_id: number
  feature_name: string
  event_source: string
  event_type: string
  message: string
  status: string
  created_at: string
}
