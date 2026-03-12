import { ScrollView, StyleSheet, Text, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import ProgressBanner from '../components/ProgressBanner';
import SectionCard from '../components/SectionCard';
import type { AppStackParamList } from '../navigation/AppNavigator';
import { getPacketCompletionSummary, usePacketStore } from '../store/packetStore';

export default function ReviewScreen({ navigation }: NativeStackScreenProps<AppStackParamList, 'Review'>) {
  const { activePacket, sections } = usePacketStore();
  const { completedCount, totalCount } = getPacketCompletionSummary(sections);
  const totalDocuments = sections.reduce((count, section) => count + section.document_count, 0);

  if (!activePacket) {
    return (
      <View style={styles.centeredContainer}>
        <Text style={styles.title}>Packet Review</Text>
        <Text style={styles.body}>Create a packet and add section content before opening the review screen.</Text>
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <ProgressBanner
        title="Packet Review"
        message={`Review packet readiness for ${activePacket.offender_name} before validation and final PDF generation.`}
      />

      <View style={styles.panel}>
        <Text style={styles.sectionTitle}>Packet Summary</Text>
        <Text style={styles.metaText}>Packet ID: {activePacket.id.slice(0, 8)}</Text>
        <Text style={styles.metaText}>Offender: {activePacket.offender_name}</Text>
        <Text style={styles.metaText}>Sections complete: {completedCount} of {totalCount}</Text>
        <Text style={styles.metaText}>Queued documents: {totalDocuments}</Text>
        <Text style={styles.metaText}>Cover letter state: Generated in backend flow; review/export wiring continues in later issues.</Text>
      </View>

      <View style={styles.panel}>
        <Text style={styles.sectionTitle}>Section Review</Text>
        <Text style={styles.sectionDescription}>Use this screen to scan the packet at a glance before validation and export work is added.</Text>
        <View style={styles.list}>
          {sections.map((section) => (
            <SectionCard
              key={section.section_key}
              title={section.title}
              description={`Status: ${section.is_populated ? 'Complete' : 'Incomplete'} • Documents: ${section.document_count}`}
              onPress={() => navigation.navigate('SectionDetail', { sectionKey: section.section_key })}
            />
          ))}
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 16 },
  centeredContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24, gap: 12 },
  title: { fontSize: 28, fontWeight: '700' },
  body: { textAlign: 'center', color: '#4b5563', fontSize: 16 },
  panel: { backgroundColor: '#ffffff', borderRadius: 12, padding: 16, borderWidth: 1, borderColor: '#e5e7eb', gap: 10 },
  sectionTitle: { fontSize: 18, fontWeight: '700', color: '#111827' },
  sectionDescription: { color: '#4b5563', lineHeight: 20 },
  metaText: { color: '#111827' },
  list: { gap: 12 },
});
