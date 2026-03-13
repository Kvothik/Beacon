import type { PacketSectionKey } from '../types/packet';

export type WorkflowEventType =
  | 'scan_captured'
  | 'scan_rescan_requested'
  | 'scan_accepted'
  | 'document_uploaded'
  | 'document_attached_to_section'
  | 'packet_review_opened'
  | 'packet_export_started'
  | 'packet_export_completed'
  | 'workflow_error';

export type WorkflowEvent = {
  type: WorkflowEventType;
  timestamp: string;
  packetId?: string | null;
  sectionKey?: PacketSectionKey | null;
  metadata?: Record<string, unknown>;
};

const MAX_EVENTS = 50;
const workflowEvents: WorkflowEvent[] = [];

export function logWorkflowEvent(event: {
  type: WorkflowEventType;
  packetId?: string | null;
  sectionKey?: PacketSectionKey | null;
  metadata?: Record<string, unknown>;
}) {
  const entry: WorkflowEvent = {
    type: event.type,
    timestamp: new Date().toISOString(),
    packetId: event.packetId ?? null,
    sectionKey: event.sectionKey ?? null,
    metadata: event.metadata,
  };

  workflowEvents.unshift(entry);
  if (workflowEvents.length > MAX_EVENTS) {
    workflowEvents.length = MAX_EVENTS;
  }

  console.log('[BeaconWorkflowEvent]', entry);
  return entry;
}

export function getWorkflowEvents() {
  return [...workflowEvents];
}

export function clearWorkflowEvents() {
  workflowEvents.length = 0;
}
