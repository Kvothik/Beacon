import { useCallback, useEffect, useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';
import ProgressBanner from '../components/ProgressBanner';
import { packetService } from '../services/packetService';
import { packetStore, usePacketStore } from '../store/packetStore';
import { logWorkflowEvent } from '../utils/eventLogger';
import type { PacketPdfGenerateResponse, PacketReadinessResponse } from '../types/packet';

export default function PdfPreviewScreen() {
  const { activePacket } = usePacketStore();
  const [pdfResult, setPdfResult] = useState<PacketPdfGenerateResponse | null>(null);
  const [readiness, setReadiness] = useState<PacketReadinessResponse | null>(null);
  const [isLoadingReadiness, setIsLoadingReadiness] = useState(false);
  const [readinessError, setReadinessError] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);

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

  async function handleGeneratePdf() {
    if (!activePacket || !readiness?.is_ready) {
      return;
    }

    setIsGenerating(true);
    setGenerationError(null);
    logWorkflowEvent({
      type: 'packet_export_started',
      packetId: activePacket.id,
      metadata: { source: 'pdf_preview' },
    });

    try {
      const response = await packetService.generatePdf(activePacket.id);
      setPdfResult(response);
      packetStore.updateActivePacket({ status: response.status === 'ready' ? 'ready' : 'generating_pdf' });
      if (response.status === 'ready') {
        logWorkflowEvent({
          type: 'packet_export_completed',
          packetId: activePacket.id,
          metadata: { pdfUrl: response.pdf_url, generatedAt: response.generated_at },
        });
      }
    } catch (error) {
      setPdfResult(null);
      setGenerationError(error instanceof Error ? error.message : 'Unable to generate the packet PDF right now.');
    } finally {
      setIsGenerating(false);
    }
  }

  if (!activePacket) {
    return (
      <View style={styles.centeredContainer}>
        <Text style={styles.title}>PDF Export</Text>
        <Text style={styles.body}>Create a packet and complete the review flow before starting PDF generation.</Text>
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <ProgressBanner
        title="PDF Export"
        message={
          pdfResult?.status === 'ready'
            ? `The packet PDF for ${activePacket.offender_name} is ready.`
            : readiness?.is_ready
              ? `Validation is complete. You can generate the final packet PDF for ${activePacket.offender_name}.`
              : `This packet still has validation blockers. Resolve them before final PDF generation for ${activePacket.offender_name}.`
        }
      />

      <View style={[styles.panel, readiness?.is_ready ? styles.readyPanel : styles.warningPanel]}>
        <Text style={styles.sectionTitle}>Export Status</Text>
        <Text style={styles.metaText}>Packet ID: {activePacket.id.slice(0, 8)}</Text>
        <Text style={styles.metaText}>Offender: {activePacket.offender_name}</Text>
        <Text style={styles.metaText}>Packet status: {pdfResult?.status ?? activePacket.status}</Text>
        <Text style={styles.metaText}>Validation status: {readiness?.is_ready ? 'Ready for PDF' : 'Blocked for final PDF'}</Text>
        {pdfResult?.generated_at ? <Text style={styles.metaText}>Generated at: {pdfResult.generated_at}</Text> : null}
        <Pressable style={styles.secondaryButton} onPress={() => loadReadiness()} disabled={isLoadingReadiness}>
          <Text style={styles.secondaryButtonText}>{isLoadingReadiness ? 'Refreshing…' : 'Refresh Validation'}</Text>
        </Pressable>
        <Pressable
          style={[styles.primaryButton, (!readiness?.is_ready || isGenerating || isLoadingReadiness) && styles.primaryButtonDisabled]}
          onPress={handleGeneratePdf}
          disabled={!readiness?.is_ready || isGenerating || isLoadingReadiness}
        >
          <Text style={styles.primaryButtonText}>
            {isGenerating ? 'Generating PDF…' : pdfResult ? 'Generate Again' : 'Generate Final PDF'}
          </Text>
        </Pressable>
        {isLoadingReadiness ? <LoadingState label="Loading readiness validation…" /> : null}
        {isGenerating ? <LoadingState label="Generating final packet PDF…" /> : null}
        {readinessError ? <ErrorState message={readinessError} /> : null}
        {generationError ? <ErrorState message={generationError} /> : null}
      </View>

      <View style={styles.panel}>
        <Text style={styles.sectionTitle}>Before You Export</Text>
        {pdfResult?.status === 'ready' ? (
          <View style={styles.successState}>
            <Text style={styles.successTitle}>PDF ready</Text>
            <Text style={styles.successMessage}>The backend returned a ready PDF artifact for this packet.</Text>
            <Text style={styles.urlLabel}>PDF URL</Text>
            <Text selectable style={styles.urlValue}>{pdfResult.pdf_url}</Text>
          </View>
        ) : !readiness?.is_ready ? (
          <View style={styles.messageList}>
            {blockingItems.map((item) => (
              <View key={item} style={styles.hintItem}>
                <Text style={styles.hintBullet}>•</Text>
                <Text style={styles.hintText}>{item}</Text>
              </View>
            ))}
            {blockingItems.length === 0 ? (
              <View style={styles.hintItem}>
                <Text style={styles.hintBullet}>•</Text>
                <Text style={styles.hintText}>Refresh validation to confirm the latest packet completion state before export.</Text>
              </View>
            ) : null}
          </View>
        ) : (
          <View style={styles.messageList}>
            <View style={styles.hintItem}>
              <Text style={styles.hintBullet}>•</Text>
              <Text style={styles.hintText}>Validation is complete and the packet is ready for final PDF generation.</Text>
            </View>
            <View style={styles.hintItem}>
              <Text style={styles.hintBullet}>•</Text>
              <Text style={styles.hintText}>Generate the PDF here when you are ready to export the packet.</Text>
            </View>
          </View>
        )}
      </View>
    </ScrollView>
  );
}

function formatMissingItem(item: string) {
  if (item === 'cover_letter') {
    return 'Generate the cover letter before exporting the final packet PDF.';
  }

  if (item.startsWith('section:')) {
    return `${formatSectionKey(item.replace('section:', ''))} is still marked incomplete.`;
  }

  if (item.startsWith('documents:')) {
    return `${formatSectionKey(item.replace('documents:', ''))} still needs at least one uploaded or scanned document.`;
  }

  return item;
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
  panel: { backgroundColor: '#ffffff', borderRadius: 12, padding: 16, borderWidth: 1, borderColor: '#e5e7eb', gap: 12 },
  readyPanel: { borderColor: '#a7f3d0', backgroundColor: '#ecfdf5' },
  warningPanel: { borderColor: '#fde68a', backgroundColor: '#fffbeb' },
  sectionTitle: { fontSize: 18, fontWeight: '700', color: '#111827' },
  metaText: { color: '#111827' },
  primaryButton: { alignItems: 'center', paddingVertical: 14, borderRadius: 12, backgroundColor: '#111827' },
  secondaryButton: { alignItems: 'center', paddingVertical: 12, borderRadius: 12, borderWidth: 1, borderColor: '#d1d5db', backgroundColor: '#ffffff' },
  secondaryButtonText: { color: '#111827', fontWeight: '600' },
  primaryButtonDisabled: { opacity: 0.6 },
  primaryButtonText: { color: '#ffffff', fontWeight: '700' },
  messageList: { gap: 10 },
  hintItem: { flexDirection: 'row', gap: 8, alignItems: 'flex-start' },
  hintBullet: { color: '#1f2937', fontSize: 16, lineHeight: 20 },
  hintText: { color: '#111827', flex: 1, lineHeight: 20 },
  successState: { backgroundColor: '#ecfdf5', borderColor: '#a7f3d0', borderWidth: 1, borderRadius: 12, padding: 14, gap: 6 },
  successTitle: { color: '#065f46', fontWeight: '700', fontSize: 16 },
  successMessage: { color: '#065f46' },
  urlLabel: { marginTop: 6, color: '#065f46', fontWeight: '700' },
  urlValue: { color: '#065f46' },
});
