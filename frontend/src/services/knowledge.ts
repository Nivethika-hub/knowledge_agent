import { apiClient } from '@/services/client'
import type { KnowledgeNode } from '@/types/api'

export async function getKnowledgeNodes(): Promise<KnowledgeNode[]> {
  const { data } = await apiClient.get<KnowledgeNode[]>('/knowledge')
  return data
}
