import { apiClient } from '@/services/client'
import type { SourceEvent, TimelineItem } from '@/types/api'

function toTimelineItem(event: SourceEvent, platform: TimelineItem['platform']): TimelineItem {
  const timestamp = event.event_time ?? event.message_time ?? event.created_at ?? event.updated_at ?? ''
  return {
    timestamp,
    platform,
    title: event.title ?? event.message ?? event.description ?? `${platform} activity`,
    feature: event.related_feature ?? 'Uncategorized',
  }
}

export async function getTimeline(): Promise<TimelineItem[]> {
  const [slack, jira, github, notion] = await Promise.all([
    apiClient.get<SourceEvent[]>('/slack'),
    apiClient.get<SourceEvent[]>('/jira'),
    apiClient.get<SourceEvent[]>('/github'),
    apiClient.get<SourceEvent[]>('/notion'),
  ])

  return [
    ...slack.data.map((event) => toTimelineItem(event, 'Slack')),
    ...jira.data.map((event) => toTimelineItem(event, 'Jira')),
    ...github.data.map((event) => toTimelineItem(event, 'GitHub')),
    ...notion.data.map((event) => toTimelineItem(event, 'Notion')),
  ].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
}
