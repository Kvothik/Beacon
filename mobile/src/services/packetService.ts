import { apiRequest } from './apiClient';
import type {
  PacketCreateRequest,
  PacketPdfGenerateResponse,
  PacketReadinessResponse,
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

  async getReadiness(packetId: string) {
    return apiRequest<PacketReadinessResponse>(`/packets/${encodeURIComponent(packetId)}/readiness`);
  },

  async generatePdf(packetId: string) {
    return apiRequest<PacketPdfGenerateResponse>(`/packets/${encodeURIComponent(packetId)}/pdf`, {
      method: 'POST',
    });
  },
};
