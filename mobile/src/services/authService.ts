import { apiRequest } from './apiClient';
import { authStore } from '../store/authStore';
import type { AuthResponse, AuthSession } from '../types/auth';

export type RegisterPayload = {
  email: string;
  password: string;
  full_name: string;
};

export type LoginPayload = {
  email: string;
  password: string;
};

function toSession(response: AuthResponse): AuthSession {
  return {
    user: response.user,
    accessToken: response.access_token,
    tokenType: response.token_type,
  };
}

export const authService = {
  async hydrateSession() {
    await authStore.hydrate();
  },

  async login(payload: LoginPayload) {
    const response = await apiRequest<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    const session = toSession(response);
    await authStore.setSession(session);
    return session;
  },

  async register(payload: RegisterPayload) {
    const response = await apiRequest<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    const session = toSession(response);
    await authStore.setSession(session);
    return session;
  },

  async logout() {
    await authStore.clearSession();
  },
};
