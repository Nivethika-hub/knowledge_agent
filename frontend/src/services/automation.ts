import { apiClient } from '@/services/client'
import type { AutomationResult } from '@/types/api'

export async function runAutomation(): Promise<AutomationResult> {
  const { data } = await apiClient.post<AutomationResult>('/automation/run')
  return data
}
