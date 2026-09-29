import { apiClient } from './client';
import type { PaginatedResponse } from '../types/common';
import type { Conversation, ConversationTurn, TraceStep } from '../types/conversation';

export const apiConversationService = {
  async getConversations(params?: any): Promise<PaginatedResponse<Conversation>> {
    return apiClient.get('/conversations', { params });
  },

  async getConversation(id: string): Promise<Conversation> {
    return apiClient.get(`/conversations/${id}`);
  },

  async getConversationTurns(conversationId: string): Promise<ConversationTurn[]> {
    return apiClient.get(`/conversations/${conversationId}/turns`);
  },

  async getTraceSteps(turnId: string): Promise<TraceStep[]> {
    return apiClient.get(`/turns/${turnId}/trace`);
  },

  async exportConversation(id: string, format: 'json' | 'txt'): Promise<Blob> {
    return apiClient.get(`/conversations/${id}/export`, {
      params: { format },
    } as any);
  },
};
