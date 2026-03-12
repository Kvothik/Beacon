export const API_BASE_URL = 'http://localhost:8000/api/v1';

export async function apiRequest<T>(_path: string, _init?: RequestInit): Promise<T> {
  throw new Error('API client scaffold only. Network requests are not implemented in issue #3.');
}
