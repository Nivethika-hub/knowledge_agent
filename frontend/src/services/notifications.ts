import { apiClient } from '@/services/client'
import type { Notification } from '@/types/api'

export async function getNotifications(): Promise<Notification[]> {
  const { data } = await apiClient.get<Notification[]>('/notifications')
  return data
}
