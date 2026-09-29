import { apiClient } from './client'
import type { DashboardStats, TrendData, AgentRanking, Alert, ResourceUsage } from '../types/dashboard'

export const apiDashboardService = {
  async getDashboardStats(): Promise<DashboardStats> {
    try {
      return await apiClient.get('/dashboard/stats')
    } catch {
      // 真实后端未提供时展示真实零值，杜绝模拟数据展示
      return {
        todayCalls: 0,
        todayCallsTrend: 0,
        tokenUsage: 0,
        tokenUsageTrend: 0,
        cost: 0,
        costTrend: 0,
        activeAgents: 0,
        totalAgents: 0,
        activeAgentsTrend: 0,
      }
    }
  },

  async getTrendData(): Promise<TrendData[]> {
    try {
      return await apiClient.get('/dashboard/trends')
    } catch {
      return []
    }
  },

  async getTopAgents(): Promise<AgentRanking[]> {
    try {
      return await apiClient.get('/dashboard/top-agents')
    } catch {
      return []
    }
  },

  async getRecentAlerts(): Promise<Alert[]> {
    try {
      return await apiClient.get('/dashboard/recent-alerts')
    } catch {
      return []
    }
  },

  async getResourceUsage(): Promise<ResourceUsage[]> {
    try {
      return await apiClient.get('/dashboard/resource-usage')
    } catch {
      return [
        { name: 'API 并发', used: 0, total: 100, percentage: 0, unit: 'QPS' },
        { name: '存储空间', used: 0, total: 50, percentage: 0, unit: 'GB' },
        { name: '向量索引', used: 0, total: 100000, percentage: 0, unit: '条' },
      ]
    }
  },
}
