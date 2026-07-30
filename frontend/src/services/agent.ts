import { apiClient } from '@/services/client'
import type { AgentAnswer } from '@/types/api'

export async function askAgent(question: string): Promise<AgentAnswer> {
  const { data } = await apiClient.post<AgentAnswer>('/agent/ask', { question })
  return data
}
