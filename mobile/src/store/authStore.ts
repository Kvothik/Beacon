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
    console.log('[authStore] hydrate start');
    if (state.isHydrated) {
      console.log('[authStore] already hydrated');
      return;
    }

    try {
      const storedSession = await AsyncStorage.getItem(AUTH_SESSION_STORAGE_KEY);
      if (!storedSession) {
        setState({ isHydrated: true, isAuthenticated: false, session: null });
        console.log('[authStore] no stored session');
        return;
      }

      const session = JSON.parse(storedSession) as AuthSession;
      setState({ isHydrated: true, isAuthenticated: true, session });
      console.log('[authStore] session restored');
    } catch (error) {
      console.log('[authStore] hydrate error:', error);
      setState({ isHydrated: true, isAuthenticated: false, session: null });
    } finally {
      console.log('[authStore] hydrate finally');
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

// Temporary logging for hydration debugging
console.log('[authStore] Initial state:', state);
authStore.subscribe(() => {
  console.log('[authStore] State change:', authStore.getState());
});
