import { apiRequest } from './apiClient';
import type { OffenderDetail, OffenderSearchRequest, OffenderSearchResponse } from '../types/offender';

function normalizeSearchPayload(payload: OffenderSearchRequest): OffenderSearchRequest {
  return {
    last_name: payload.last_name?.trim() || null,
    first_name_initial: payload.first_name_initial?.trim().slice(0, 1) || null,
    tdcj_number: payload.tdcj_number?.trim() || null,
    sid: payload.sid?.trim() || null,
    page: payload.page ?? 1,
  };
}

export const offenderService = {
  async search(payload: OffenderSearchRequest) {
    return apiRequest<OffenderSearchResponse>('/offenders/search', {
      method: 'POST',
      body: JSON.stringify(normalizeSearchPayload(payload)),
    });
  },

  async getDetail(sid: string) {
    return apiRequest<OffenderDetail>(`/offenders/${encodeURIComponent(sid)}`);
  },
};
