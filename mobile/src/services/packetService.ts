import { apiRequest } from './apiClient';
import type {
  PacketCreateRequest,
  PacketSectionKey,
  PacketSectionUpdateRequest,
  PacketSectionUpdateResponse,
  PacketSummary,
  PacketUploadCreateRequest,
  PacketUploadCreateResponse,
} from '../types/packet';

export const packetService = {
  async create(payload: PacketCreateRequest) {
    return apiRequest<PacketSummary>('/packets', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async updateSection(packetId: string, sectionKey: PacketSectionKey, payload: PacketSectionUpdateRequest) {
    return apiRequest<PacketSectionUpdateResponse>(`/packets/${encodeURIComponent(packetId)}/sections/${encodeURIComponent(sectionKey)}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
  },

  async createUpload(packetId: string, payload: PacketUploadCreateRequest) {
    return apiRequest<PacketUploadCreateResponse>(`/packets/${encodeURIComponent(packetId)}/uploads`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
};
