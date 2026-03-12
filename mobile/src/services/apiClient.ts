import { getAuthSession } from '../store/authStore';
import type { ApiError } from '../types/api';

export const API_BASE_URL = 'http://localhost:8000/api/v1';

export class ApiClientError extends Error {
  code: string;
  details: unknown;
  retryable: boolean;
  status: number;

  constructor(status: number, payload: ApiError) {
    super(payload.error.message);
    this.name = 'ApiClientError';
    this.status = status;
    this.code = payload.error.code;
    this.details = payload.error.details;
    this.retryable = payload.error.retryable;
  }
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const session = getAuthSession();
  const headers = new Headers(init.headers ?? {});
  headers.set('Content-Type', 'application/json');
  if (session?.accessToken) {
    headers.set('Authorization', `Bearer ${session.accessToken}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  });

  if (!response.ok) {
    const payload = (await response.json()) as ApiError;
    throw new ApiClientError(response.status, payload);
  }

  return (await response.json()) as T;
}
