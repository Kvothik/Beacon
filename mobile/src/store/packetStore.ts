import { useSyncExternalStore } from 'react';

import type { PacketSectionKey, PacketSectionState, PacketSummary } from '../types/packet';

export type PacketStoreState = {
  activePacket: PacketSummary | null;
  sections: PacketSectionState[];
};

export function getPacketCompletionSummary(sections: PacketSectionState[]) {
  const completedCount = sections.filter((section) => section.is_populated).length;
  return {
    completedCount,
    totalCount: sections.length,
  };
}

const DEFAULT_PACKET_SECTIONS: PacketSectionState[] = [
  { section_key: 'photos', title: 'Photos', is_populated: false, notes_text: null, sort_order: 1 },
  { section_key: 'support_letters', title: 'Support Letters', is_populated: false, notes_text: null, sort_order: 2 },
  { section_key: 'reflection_letter', title: 'Reflection Letter', is_populated: false, notes_text: null, sort_order: 3 },
  { section_key: 'certificates_and_education', title: 'Certificates and Education', is_populated: false, notes_text: null, sort_order: 4 },
  { section_key: 'future_employment', title: 'Future Employment', is_populated: false, notes_text: null, sort_order: 5 },
  { section_key: 'parole_plan', title: 'Parole Plan', is_populated: false, notes_text: null, sort_order: 6 },
  { section_key: 'court_and_case_documents', title: 'Court and Case Documents', is_populated: false, notes_text: null, sort_order: 7 },
  { section_key: 'other_miscellaneous', title: 'Other or Miscellaneous', is_populated: false, notes_text: null, sort_order: 8 },
];

let state: PacketStoreState = {
  activePacket: null,
  sections: DEFAULT_PACKET_SECTIONS,
};

const listeners = new Set<() => void>();

function emitChange() {
  listeners.forEach((listener) => listener());
}

function setState(nextState: PacketStoreState) {
  state = nextState;
  emitChange();
}

export const packetStore = {
  getState(): PacketStoreState {
    return state;
  },

  subscribe(listener: () => void) {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },

  setActivePacket(packet: PacketSummary) {
    setState({
      activePacket: packet,
      sections: DEFAULT_PACKET_SECTIONS.map((section) => ({ ...section })),
    });
  },

  updateSection(sectionKey: PacketSectionKey, patch: Partial<PacketSectionState>) {
    setState({
      ...state,
      sections: state.sections.map((section) =>
        section.section_key === sectionKey ? { ...section, ...patch } : section,
      ),
    });
  },

  getSection(sectionKey: PacketSectionKey) {
    return state.sections.find((section) => section.section_key === sectionKey) ?? null;
  },

  reset() {
    setState({
      activePacket: null,
      sections: DEFAULT_PACKET_SECTIONS.map((section) => ({ ...section })),
    });
  },
};

export function usePacketStore(): PacketStoreState {
  return useSyncExternalStore(packetStore.subscribe, packetStore.getState, packetStore.getState);
}
