import { useCallback, useEffect, useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';
import ProgressBanner from '../components/ProgressBanner';
import SectionCard from '../components/SectionCard';
import type { AppStackParamList } from '../navigation/AppNavigator';
import { packetService } from '../services/packetService';
import { getPacketCompletionSummary, usePacketStore } from '../store/packetStore';
import type { PacketReadinessResponse } from '../types/packet';

export default function ReviewScreen({ navigation }: NativeStackScreenProps<AppStackParamList, 'Review'>) {
  const { activePacket, sections } = usePacketStore();
  const { completedCount, totalCount } = getPacketCompletionSummary(sections);
  const totalDocuments = sections.reduce((count, section) => count + section.document_count, 0);
  const [readiness, setReadiness] = useState<PacketReadinessResponse | null>(null);
  const [isLoadingReadiness, setIsLoadingReadiness] = useState(false);
  const [readinessError, setReadinessError] = useState<string | null>(null);

  const loadReadiness = useCallback(async () => {
    if (!activePacket) {
      setReadiness(null);
      setReadinessError(null);
      return;
    }

    setIsLoadingReadiness(true);
    setReadinessError(null);

    try {
      const response = await packetService.getReadiness(activePacket.id);
      setReadiness(response);
    } catch (error) {
      setReadiness(null);
      setReadinessError(error instanceof Error ? error.message : 'Unable to load packet readiness right now.');
    } finally {
      setIsLoadingReadiness(false);
    }
  }, [activePacket]);

  useEffect(() => {
    loadReadiness().catch(() => {
      // state is already handled inside loadReadiness
    });
  }, [loadReadiness]);

  const blockingItems = useMemo(() => {
    if (!readiness) {
      return [];
    }

    return readiness.missing_items.map(formatMissingItem);
  }, [readiness]);

  const readinessCounts = useMemo(() => {
    if (!readiness) {
      return {
        incompleteSections: 0,
        missingDocuments: 0,
        missingCoverLetter: false,
      };
    }

    return {
      incompleteSections: readiness.missing_items.filter((item) => item.startsWith('section:')).length,
      missingDocuments: readiness.missing_items.filter((item) => item.startsWith('documents:')).length,
      missingCoverLetter: readiness.missing_items.includes('cover_letter'),
    };
  }, [readiness]);

  const completedItems = useMemo(() => {
    if (!readiness) {
      return [];
    }

    const missing = new Set(readiness.missing_items);
    const items: string[] = [];

    if (!missing.has('cover_letter')) {
      items.push('Cover letter is already generated.');
    }

    if (completedCount > 0) {
      items.push(`${completedCount} ${completedCount === 1 ? 'section is' : 'sections are'} already marked complete.`);
    }

    if (totalDocuments > 0) {
      items.push(`${totalDocuments} ${totalDocuments === 1 ? 'document is' : 'documents are'} already attached across the packet.`);
    }

    if (items.length === 0) {
      items.push('You can keep building the packet section by section. Nothing is lost if validation is still incomplete.');
    }

    return items;
  }, [completedCount, readiness, totalDocuments]);

  const nextStepHints = useMemo(() => {
    if (!readiness) {
      return [];
    }

    const missing = new Set(readiness.missing_items);
    const hints: string[] = [];

    if (missing.has('cover_letter')) {
      hints.push('Generate the cover letter before final PDF export.');
    }

    if (Array.from(missing).some((item) => item.startsWith('section:'))) {
      hints.push('Open incomplete sections and add enough notes to mark them complete when ready.');
    }

    if (Array.from(missing).some((item) => item.startsWith('documents:'))) {
      hints.push('Add at least one uploaded or scanned document to each section that still shows missing documents.');
    }

    if (hints.length === 0) {
      hints.push('Readiness checks look good. You can stay in review or continue to the final export flow when it is available.');
    }

    return hints;
  }, [readiness]);

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
        message={
          readiness?.is_ready
            ? `Packet is ready for final export for ${activePacket.offender_name}.`
            : `This packet is not ready for final PDF generation yet. Review the blocking items, then continue building for ${activePacket.offender_name}.`
        }
      />

      <View style={[styles.panel, readiness?.is_ready ? styles.readyPanel : styles.warningPanel]}>
        <Text style={styles.sectionTitle}>Validation Summary</Text>
        <Text style={styles.metaText}>Packet ID: {activePacket.id.slice(0, 8)}</Text>
        <Text style={styles.metaText}>Offender: {activePacket.offender_name}</Text>
        <Text style={styles.metaText}>Sections complete: {completedCount} of {totalCount}</Text>
        <Text style={styles.metaText}>Queued documents: {totalDocuments}</Text>
        <Text style={styles.metaText}>Validation status: {readiness?.is_ready ? 'Ready for PDF' : 'Blocked for final PDF'}</Text>
        {readiness && !readiness.is_ready ? (
          <View style={styles.summaryList}>
            {readinessCounts.missingCoverLetter ? <Text style={styles.summaryText}>• Cover letter still needs to be generated</Text> : null}
            {readinessCounts.incompleteSections > 0 ? (
              <Text style={styles.summaryText}>• {readinessCounts.incompleteSections} {readinessCounts.incompleteSections === 1 ? 'section is' : 'sections are'} still marked incomplete</Text>
            ) : null}
            {readinessCounts.missingDocuments > 0 ? (
              <Text style={styles.summaryText}>• {readinessCounts.missingDocuments} {readinessCounts.missingDocuments === 1 ? 'section is' : 'sections are'} still missing a document</Text>
            ) : null}
          </View>
        ) : null}
        <Pressable style={styles.secondaryButton} onPress={() => loadReadiness()} disabled={isLoadingReadiness}>
          <Text style={styles.secondaryButtonText}>{isLoadingReadiness ? 'Refreshing…' : 'Refresh Validation'}</Text>
        </Pressable>
      </View>

      <View style={styles.panel}>
        <Text style={styles.sectionTitle}>Blocking Items</Text>
        <Text style={styles.sectionDescription}>These items must be resolved before the packet can be considered ready for final PDF generation.</Text>
        {isLoadingReadiness ? <LoadingState label="Loading readiness validation…" /> : null}
        {readinessError ? <ErrorState message={readinessError} /> : null}
        {!isLoadingReadiness && !readinessError && blockingItems.length === 0 ? (
          <View style={styles.successState}>
            <Text style={styles.successTitle}>No blocking items</Text>
            <Text style={styles.successMessage}>The backend readiness check says this packet is ready for the final export step.</Text>
          </View>
        ) : null}
        {!isLoadingReadiness && !readinessError && blockingItems.length > 0 ? (
          <View style={styles.messageList}>
            {blockingItems.map((item) => (
              <View key={item} style={styles.blockingItem}>
                <Text style={styles.blockingBullet}>•</Text>
                <Text style={styles.blockingText}>{item}</Text>
              </View>
            ))}
          </View>
        ) : null}
      </View>

      <View style={styles.panel}>
        <Text style={styles.sectionTitle}>What Is Already Done</Text>
        <Text style={styles.sectionDescription}>These items help show progress even when the packet still has blocking validation items.</Text>
        <View style={styles.messageList}>
          {completedItems.map((item) => (
            <View key={item} style={styles.completedItem}>
              <Text style={styles.completedBullet}>•</Text>
              <Text style={styles.completedText}>{item}</Text>
            </View>
          ))}
        </View>
      </View>

      <View style={styles.panel}>
        <Text style={styles.sectionTitle}>Next Steps</Text>
        <Text style={styles.sectionDescription}>These reminders are guidance for finishing the packet; they do not replace the blocking checks above.</Text>
        <View style={styles.messageList}>
          {nextStepHints.map((item) => (
            <View key={item} style={styles.hintItem}>
              <Text style={styles.hintBullet}>•</Text>
              <Text style={styles.hintText}>{item}</Text>
            </View>
          ))}
        </View>
        <Pressable
          style={[styles.primaryButton, !readiness?.is_ready && styles.primaryButtonDisabled]}
          onPress={() => navigation.navigate('PdfPreview')}
          disabled={!readiness?.is_ready}
        >
          <Text style={styles.primaryButtonText}>{readiness?.is_ready ? 'Continue to PDF Export' : 'Resolve blocking items first'}</Text>
        </Pressable>
      </View>

      <View style={styles.panel}>
        <Text style={styles.sectionTitle}>Section Review</Text>
        <Text style={styles.sectionDescription}>Use this screen to scan the packet at a glance and jump back into any section that still needs work.</Text>
        <View style={styles.list}>
          {sections.map((section) => (
            <SectionCard
              key={section.section_key}
              title={section.title}
              description={formatSectionDescription(section, readiness?.missing_items ?? [])}
              onPress={() => navigation.navigate('SectionDetail', { sectionKey: section.section_key })}
            />
          ))}
        </View>
      </View>
    </ScrollView>
  );
}

function formatMissingItem(item: string) {
  if (item === 'cover_letter') {
    return 'Cover letter has not been generated yet.';
  }

  if (item.startsWith('section:')) {
    const sectionKey = item.replace('section:', '');
    return `${formatSectionKey(sectionKey)} is still marked incomplete.`;
  }

  if (item.startsWith('documents:')) {
    const sectionKey = item.replace('documents:', '');
    return `${formatSectionKey(sectionKey)} does not have an uploaded or scanned document yet.`;
  }

  return item;
}

function formatSectionDescription(
  section: { section_key: string; is_populated: boolean; document_count: number },
  missingItems: string[],
) {
  const blockers: string[] = [];

  if (missingItems.includes(`section:${section.section_key}`)) {
    blockers.push('needs notes or completion');
  }

  if (missingItems.includes(`documents:${section.section_key}`)) {
    blockers.push('needs document');
  }

  if (blockers.length > 0) {
    return `Blocking: ${blockers.join(' • ')}`;
  }

  const statusText = section.is_populated ? 'Complete' : 'Incomplete';
  const documentText = section.document_count === 1 ? '1 document' : `${section.document_count} documents`;
  return `Status: ${statusText} • ${documentText}`;
}

function formatSectionKey(sectionKey: string) {
  return sectionKey
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 16 },
  centeredContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24, gap: 12 },
  title: { fontSize: 28, fontWeight: '700' },
  body: { textAlign: 'center', color: '#4b5563', fontSize: 16 },
  panel: { backgroundColor: '#ffffff', borderRadius: 12, padding: 16, borderWidth: 1, borderColor: '#e5e7eb', gap: 10 },
  warningPanel: { borderColor: '#f59e0b', backgroundColor: '#fffbeb' },
  readyPanel: { borderColor: '#10b981', backgroundColor: '#ecfdf5' },
  sectionTitle: { fontSize: 18, fontWeight: '700', color: '#111827' },
  sectionDescription: { color: '#4b5563', lineHeight: 20 },
  metaText: { color: '#111827' },
  summaryList: { gap: 4, marginTop: 4 },
  summaryText: { color: '#92400e', lineHeight: 20 },
  list: { gap: 12 },
  primaryButton: { alignItems: 'center', paddingVertical: 14, borderRadius: 12, backgroundColor: '#111827' },
  primaryButtonDisabled: { opacity: 0.6 },
  primaryButtonText: { color: '#ffffff', fontWeight: '700' },
  secondaryButton: {
    alignSelf: 'flex-start',
    marginTop: 6,
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#d1d5db',
    backgroundColor: '#ffffff',
  },
  secondaryButtonText: { color: '#111827', fontWeight: '600' },
  successState: { backgroundColor: '#ecfdf5', borderColor: '#a7f3d0', borderWidth: 1, borderRadius: 12, padding: 14, gap: 6 },
  successTitle: { color: '#065f46', fontWeight: '700', fontSize: 16 },
  successMessage: { color: '#065f46' },
  messageList: { gap: 10 },
  blockingItem: { flexDirection: 'row', gap: 8, alignItems: 'flex-start' },
  blockingBullet: { color: '#991b1b', fontSize: 16, lineHeight: 20 },
  blockingText: { color: '#7f1d1d', flex: 1, lineHeight: 20 },
  completedItem: { flexDirection: 'row', gap: 8, alignItems: 'flex-start' },
  completedBullet: { color: '#065f46', fontSize: 16, lineHeight: 20 },
  completedText: { color: '#065f46', flex: 1, lineHeight: 20 },
  hintItem: { flexDirection: 'row', gap: 8, alignItems: 'flex-start' },
  hintBullet: { color: '#1f2937', fontSize: 16, lineHeight: 20 },
  hintText: { color: '#111827', flex: 1, lineHeight: 20 },
});
