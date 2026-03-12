import { useSyncExternalStore } from 'react';

import type { OffenderDetail, OffenderSearchPagination, OffenderSummary } from '../types/offender';

export type OffenderStoreState = {
  results: OffenderSummary[];
  pagination: OffenderSearchPagination | null;
  selectedOffenderSid: string | null;
  selectedOffenderDetail: OffenderDetail | null;
};

let state: OffenderStoreState = {
  results: [],
  pagination: null,
  selectedOffenderSid: null,
  selectedOffenderDetail: null,
};

const listeners = new Set<() => void>();

function emitChange() {
  listeners.forEach((listener) => listener());
}

function setState(nextState: OffenderStoreState) {
  state = nextState;
  emitChange();
}

export const offenderStore = {
  getState(): OffenderStoreState {
    return state;
  },

  subscribe(listener: () => void) {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },

  setSearchResults(results: OffenderSummary[], pagination: OffenderSearchPagination | null) {
    setState({
      ...state,
      results,
      pagination,
      selectedOffenderSid: state.selectedOffenderSid && results.some((result) => result.sid === state.selectedOffenderSid)
        ? state.selectedOffenderSid
        : null,
      selectedOffenderDetail: state.selectedOffenderSid && results.some((result) => result.sid === state.selectedOffenderSid)
        ? state.selectedOffenderDetail
        : null,
    });
  },

  setSelectedOffenderSid(sid: string | null) {
    setState({
      ...state,
      selectedOffenderSid: sid,
      selectedOffenderDetail: sid === state.selectedOffenderDetail?.sid ? state.selectedOffenderDetail : null,
    });
  },

  setSelectedOffenderDetail(detail: OffenderDetail | null) {
    setState({
      ...state,
      selectedOffenderSid: detail?.sid ?? state.selectedOffenderSid,
      selectedOffenderDetail: detail,
    });
  },

  reset() {
    setState({
      results: [],
      pagination: null,
      selectedOffenderSid: null,
      selectedOffenderDetail: null,
    });
  },
};

export function useOffenderStore(): OffenderStoreState {
  return useSyncExternalStore(offenderStore.subscribe, offenderStore.getState, offenderStore.getState);
}
