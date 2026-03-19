import AsyncStorage from '@react-native-async-storage/async-storage';
import { useSyncExternalStore } from 'react';

import type { AuthSession } from '../types/auth';

const AUTH_SESSION_STORAGE_KEY = 'beacon.auth.session';

export type AuthStoreState = {
  isHydrated: boolean;
  isAuthenticated: boolean;
  session: AuthSession | null;
};

let state: AuthStoreState = {
  isHydrated: false,
  isAuthenticated: false,
  session: null,
};

const listeners = new Set<() => void>();

function emitChange() {
  listeners.forEach((listener) => listener());
}

function setState(nextState: AuthStoreState) {
  state = nextState;
  emitChange();
}

export const authStore = {
  getState(): AuthStoreState {
    return state;
  },

  subscribe(listener: () => void) {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },

  async hydrate() {
    if (state.isHydrated) {
      return;
    }

    try {
      const storedSession = await AsyncStorage.getItem(AUTH_SESSION_STORAGE_KEY);
      if (!storedSession) {
        setState({ isHydrated: true, isAuthenticated: false, session: null });
        return;
      }

      const session = JSON.parse(storedSession) as AuthSession;
      setState({ isHydrated: true, isAuthenticated: true, session });
    } catch (error) {
      // Safely handle errors during hydration
      setState({ isHydrated: true, isAuthenticated: false, session: null });
    }
  },

  async setSession(session: AuthSession) {
    await AsyncStorage.setItem(AUTH_SESSION_STORAGE_KEY, JSON.stringify(session));
    setState({ isHydrated: true, isAuthenticated: true, session });
  },

  async clearSession() {
    await AsyncStorage.removeItem(AUTH_SESSION_STORAGE_KEY);
    setState({ isHydrated: true, isAuthenticated: false, session: null });
  },
};

export function getAuthSession(): AuthSession | null {
  return state.session;
}

export function useAuthStore(): AuthStoreState {
  return useSyncExternalStore(authStore.subscribe, authStore.getState, authStore.getState);
}
