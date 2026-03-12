import { ScrollView, StyleSheet, Text, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import ProgressBanner from '../components/ProgressBanner';
import SectionCard from '../components/SectionCard';
import type { AppStackParamList } from '../navigation/AppNavigator';
import { getPacketCompletionSummary, usePacketStore } from '../store/packetStore';

export default function PacketBuilderScreen({ navigation }: NativeStackScreenProps<AppStackParamList, 'PacketBuilder'>) {
  const { activePacket, sections } = usePacketStore();
  const { completedCount, totalCount } = getPacketCompletionSummary(sections);

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
          <Text style={styles.progressText}>{completedCount} of {totalCount} sections complete</Text>
        </View>
      ) : null}

      <View style={styles.panel}>
        <Text style={styles.sectionTitle}>Packet Sections</Text>
        <Text style={styles.sectionDescription}>Section order follows `docs/pdf_spec.md`. Completion state is shown now; editing and uploads come in later issues.</Text>
        <View style={styles.list}>
          {sections.map((section) => (
            <SectionCard
              key={section.section_key}
              title={section.title}
              description={`Section ${section.sort_order} of ${totalCount} • ${section.is_populated ? 'Complete' : 'Not started'}`}
              onPress={activePacket ? () => navigation.navigate('SectionDetail') : undefined}
            />
          ))}
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 16 },
  panel: { backgroundColor: '#ffffff', borderRadius: 12, padding: 16, borderWidth: 1, borderColor: '#e5e7eb', gap: 10 },
  sectionTitle: { fontSize: 18, fontWeight: '700', color: '#111827' },
  sectionDescription: { color: '#4b5563', lineHeight: 20 },
  metaText: { color: '#111827' },
  progressText: { color: '#2563eb', fontWeight: '600' },
  list: { gap: 12 },
});
