import { apiClient } from './client'
import type { ApiKey, AuditLog, SystemAlert, SystemSettings } from '../types/system'

// ---- 后端真实类型 ----
export interface BackendUser {
  id: number
  username: string
  email: string
  is_active: boolean
}

export interface BackendUserWithRoles extends BackendUser {
  roles: BackendRole[]
}

export interface BackendRole {
  id: number
  code: string
  name: string
  description: string | null
  permissions: BackendPermission[]
}

export interface BackendPermission {
  id: number
  code: string
  name: string
  description: string | null
}

export interface PageResult<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export const apiSystemService = {
  // ---- 用户 ----
  async getUsers(params?: { page?: number; page_size?: number; keyword?: string }): Promise<PageResult<BackendUser>> {
    return apiClient.get('/users/search', { params: params as Record<string, unknown> })
  },

  async getUser(id: number): Promise<BackendUserWithRoles> {
    const user = await apiClient.get<BackendUser>(`/users/${id}`)
    try {
      const userRoles = await apiClient.get<BackendUserWithRoles[]>(`/users/${id}/roles`)
      const roles = userRoles?.[0]?.roles || []
      return { ...user, roles }
    } catch {
      return { ...user, roles: [] }
    }
  },

  async createUser(data: { username: string; email: string; password: string }): Promise<BackendUser> {
    return apiClient.post('/users/', data)
  },

  async deleteUser(id: number): Promise<void> {
    return apiClient.delete(`/users/${id}`)
  },

  async assignUserRoles(userId: number, roleIds: number[]): Promise<BackendUser> {
    return apiClient.put(`/users/${userId}/roles`, roleIds)
  },

  async getCurrentUser(): Promise<BackendUser> {
    return apiClient.get('/users/me')
  },

  // ---- 角色 ----
  async getRoles(): Promise<BackendRole[]> {
    return apiClient.get('/roles/')
  },

  async searchRoles(params?: { page?: number; page_size?: number; keyword?: string }): Promise<PageResult<BackendRole>> {
    return apiClient.get('/roles/search', { params: params as Record<string, unknown> })
  },

  async getRole(id: number): Promise<BackendRole> {
    return apiClient.get(`/roles/${id}`)
  },

  async createRole(data: { code: string; name: string; description?: string }): Promise<BackendRole> {
    return apiClient.post('/roles/', data)
  },

  async updateRole(id: number, data: { name?: string; description?: string }): Promise<BackendRole> {
    return apiClient.put(`/roles/${id}`, data)
  },

  async deleteRole(id: number): Promise<void> {
    return apiClient.delete(`/roles/${id}`)
  },

  async assignRolePermissions(roleId: number, permissionIds: number[]): Promise<BackendRole> {
    return apiClient.put(`/roles/${roleId}/permissions`, { permission_ids: permissionIds })
  },

  // ---- 权限 ----
  async getPermissions(): Promise<BackendPermission[]> {
    return apiClient.get('/permissions/')
  },

  async searchPermissions(params?: { page?: number; page_size?: number; keyword?: string }): Promise<PageResult<BackendPermission>> {
    return apiClient.get('/permissions/search', { params: params as Record<string, unknown> })
  },

  async createPermission(data: { code: string; name: string; description?: string }): Promise<BackendPermission> {
    return apiClient.post('/permissions/', data)
  },

  async updatePermission(id: number, data: { name?: string; description?: string }): Promise<BackendPermission> {
    return apiClient.put(`/permissions/${id}`, data)
  },

  async deletePermission(id: number): Promise<void> {
    return apiClient.delete(`/permissions/${id}`)
  },

  // ---- 扩展系统管理（非Mock模式下若后端未开发则显示空数据，杜绝模拟数据展示） ----
  async getApiKeys(params?: { page?: number; pageSize?: number; status?: string }): Promise<{ data: ApiKey[]; total: number; page: number; pageSize: number }> {
    try {
      return await apiClient.get('/system/api-keys', { params: params as Record<string, unknown> })
    } catch {
      return { data: [], total: 0, page: params?.page || 1, pageSize: params?.pageSize || 10 }
    }
  },

  async createApiKey(data: Partial<ApiKey>): Promise<ApiKey> {
    return apiClient.post('/system/api-keys', data)
  },

  async deleteApiKey(id: string): Promise<void> {
    return apiClient.delete(`/system/api-keys/${id}`)
  },

  async getAuditLogs(params?: { page?: number; pageSize?: number }): Promise<{ data: AuditLog[]; total: number; page: number; pageSize: number }> {
    try {
      return await apiClient.get('/system/audit-logs', { params: params as Record<string, unknown> })
    } catch {
      return { data: [], total: 0, page: params?.page || 1, pageSize: params?.pageSize || 10 }
    }
  },

  async getSystemAlerts(params?: { page?: number; pageSize?: number }): Promise<{ data: SystemAlert[]; total: number; page: number; pageSize: number }> {
    try {
      return await apiClient.get('/system/alerts', { params: params as Record<string, unknown> })
    } catch {
      return { data: [], total: 0, page: params?.page || 1, pageSize: params?.pageSize || 10 }
    }
  },

  async acknowledgeAlert(id: string): Promise<void> {
    return apiClient.post(`/system/alerts/${id}/acknowledge`)
  },

  async resolveAlert(id: string): Promise<void> {
    return apiClient.post(`/system/alerts/${id}/resolve`)
  },

  async getSettings(): Promise<SystemSettings> {
    try {
      return await apiClient.get('/system/settings')
    } catch {
      return {
        systemName: '辰光 Agent',
        systemDescription: '企业级智能Agent管理平台',
        defaultLanguage: 'zh-CN',
        defaultModel: 'qwen-max',
        defaultTemperature: 0.7,
        defaultMaxTokens: 2048,
        smtpServer: '',
        smtpPort: 25,
        senderEmail: '',
      }
    }
  },

  async updateSettings(data: Partial<SystemSettings>): Promise<SystemSettings> {
    return apiClient.put('/system/settings', data)
  },
}
