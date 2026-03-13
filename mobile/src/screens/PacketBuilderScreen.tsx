import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import ProgressBanner from '../components/ProgressBanner';
import SectionCard from '../components/SectionCard';
import type { AppStackParamList } from '../navigation/AppNavigator';
import { getPacketCompletionSummary, usePacketStore } from '../store/packetStore';
import { logWorkflowEvent } from '../utils/eventLogger';

export default function PacketBuilderScreen({ navigation }: NativeStackScreenProps<AppStackParamList, 'PacketBuilder'>) {
  const { activePacket, sections, recentDocuments } = usePacketStore();
  const { completedCount, totalCount } = getPacketCompletionSummary(sections);
  const completeSections = sections.filter((section) => getSectionProgressState(section) === 'complete').length;
  const partialSections = sections.filter((section) => getSectionProgressState(section) === 'partial').length;
  const incompleteSections = sections.filter((section) => getSectionProgressState(section) === 'incomplete').length;
  const progressPercent = totalCount === 0 ? 0 : Math.round(((completeSections + partialSections * 0.5) / totalCount) * 100);

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <ProgressBanner
        title="Packet Builder"
        message={
          activePacket
            ? `Packet ${activePacket.id.slice(0, 8)} is ready to build for ${activePacket.offender_name}.`
            : 'No active packet yet. Create a packet from the offender detail screen first.'
        }
      />

      {activePacket ? (
        <View style={styles.panel}>
          <Text style={styles.sectionTitle}>Packet Summary</Text>
          <Text style={styles.metaText}>Status: {activePacket.status}</Text>
          <Text style={styles.metaText}>Offender: {activePacket.offender_name}</Text>
          <Text style={styles.metaText}>SID: {activePacket.offender_sid}</Text>
          <Text style={styles.metaText}>Parole Board Office: {activePacket.parole_board_office_code ?? 'Not available'}</Text>
          <Text style={styles.progressText}>{completedCount} of {totalCount} sections marked complete</Text>
          <Text style={styles.progressText}>Overall packet progress: {progressPercent}%</Text>
          <View style={styles.progressBarTrack}>
            <View style={[styles.progressBarFill, { width: `${progressPercent}%` }]} />
          </View>
          <View style={styles.progressLegend}>
            <Text style={styles.progressLegendText}>Complete: {completeSections}</Text>
            <Text style={styles.progressLegendText}>Partial: {partialSections}</Text>
            <Text style={styles.progressLegendText}>Incomplete: {incompleteSections}</Text>
          </View>
        </View>
      ) : (
        <View style={styles.panel}>
          <Text style={styles.sectionTitle}>No active packet</Text>
          <Text style={styles.sectionDescription}>Packet builder cannot continue until a packet is created from offender search.</Text>
          <Pressable style={styles.recoveryButton} onPress={() => navigation.navigate('Home')}>
            <Text style={styles.recoveryButtonText}>Return to Offender Search</Text>
          </Pressable>
        </View>
      )}

      <View style={styles.panel}>
        <Text style={styles.sectionTitle}>Packet Sections</Text>
        <Text style={styles.sectionDescription}>Open a section to edit notes and completion state. Uploads and scanner attachments arrive in later issues.</Text>
        <SectionCard
          title="Open Packet Review"
          description="Review current section completion, uploads, and cover letter state"
          onPress={() => {
            if (activePacket) {
              logWorkflowEvent({
                type: 'packet_review_opened',
                packetId: activePacket.id,
                metadata: { source: 'packet_builder' },
              });
            }
            navigation.navigate('Review');
          }}
        />
        <View style={styles.list}>
          {sections.map((section) => (
            <SectionCard
              key={section.section_key}
              title={formatSectionCardTitle(section)}
              description={formatSectionCardDescription(section, totalCount, recentDocuments)}
              onPress={activePacket ? () => navigation.navigate('SectionDetail', { sectionKey: section.section_key }) : undefined}
            />
          ))}
        </View>
      </View>
    </ScrollView>
  );
}

function getSectionProgressState(section: { is_populated: boolean; document_count?: number }) {
  const hasDocuments = (section.document_count ?? 0) > 0;
  if (section.is_populated && hasDocuments) {
    return 'complete';
  }
  if (section.is_populated || hasDocuments) {
    return 'partial';
  }
  return 'incomplete';
}

function formatSectionCardTitle(section: { title: string; is_populated: boolean; document_count?: number }) {
  const state = getSectionProgressState(section);
  const prefix = state === 'complete' ? '●' : state === 'partial' ? '◐' : '○';
  return `${prefix} ${section.title}`;
}

function formatSectionCardDescription(section: { section_key: string; sort_order: number; is_populated: boolean; document_count?: number }, totalCount: number, recentDocuments: { section_key: string; filename: string; source: string }[]) {
  const latestDocument = recentDocuments.find((item) => item.section_key === section.section_key);
  const state = getSectionProgressState(section);
  const stateLabel = state === 'complete' ? 'Complete' : state === 'partial' ? 'Partially complete' : 'Incomplete';
  const parts = [
    `Section ${section.sort_order} of ${totalCount}`,
    stateLabel,
    latestDocument ? `Latest doc: ${latestDocument.filename} (${latestDocument.source})` : 'No visible attachment yet',
  ];
  return parts.join(' • ');
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 16 },
  panel: { backgroundColor: '#ffffff', borderRadius: 12, padding: 16, borderWidth: 1, borderColor: '#e5e7eb', gap: 10 },
  sectionTitle: { fontSize: 18, fontWeight: '700', color: '#111827' },
  sectionDescription: { color: '#4b5563', lineHeight: 20 },
  metaText: { color: '#111827' },
  progressText: { color: '#2563eb', fontWeight: '600' },
  progressBarTrack: { height: 10, borderRadius: 999, backgroundColor: '#dbeafe', overflow: 'hidden' },
  progressBarFill: { height: '100%', borderRadius: 999, backgroundColor: '#2563eb' },
  progressLegend: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  progressLegendText: { color: '#374151', fontSize: 13, fontWeight: '600' },
  recoveryButton: { alignItems: 'center', paddingVertical: 14, borderRadius: 12, borderWidth: 1, borderColor: '#d1d5db', backgroundColor: '#ffffff' },
  recoveryButtonText: { color: '#111827', fontWeight: '700' },
  list: { gap: 12 },
});
