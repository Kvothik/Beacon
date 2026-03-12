import { apiRequest } from './apiClient';
import type { PacketCreateRequest, PacketSummary } from '../types/packet';

export const packetService = {
  async create(payload: PacketCreateRequest) {
    return apiRequest<PacketSummary>('/packets', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
};
