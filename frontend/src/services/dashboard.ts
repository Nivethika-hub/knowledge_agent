import { apiClient } from '@/services/client'
import type { KnowledgeNode, Project, SourceEvent, TeamMember } from '@/types/api'

export interface DashboardData {
  projects: Project[]
  teamMembers: TeamMember[]
  slackMessages: SourceEvent[]
  jiraTickets: SourceEvent[]
  githubEvents: SourceEvent[]
  knowledgeNodes: KnowledgeNode[]
}

export async function getDashboardData(): Promise<DashboardData> {
  const [projects, teamMembers, slackMessages, jiraTickets, githubEvents, knowledgeNodes] =
    await Promise.all([
      apiClient.get<Project[]>('/projects'),
      apiClient.get<TeamMember[]>('/team-members'),
      apiClient.get<SourceEvent[]>('/slack'),
      apiClient.get<SourceEvent[]>('/jira'),
      apiClient.get<SourceEvent[]>('/github'),
      apiClient.get<KnowledgeNode[]>('/knowledge'),
    ])

  return {
    projects: projects.data,
    teamMembers: teamMembers.data,
    slackMessages: slackMessages.data,
    jiraTickets: jiraTickets.data,
    githubEvents: githubEvents.data,
    knowledgeNodes: knowledgeNodes.data,
  }
}
