import { useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';
import ProgressBanner from '../components/ProgressBanner';
import { packetService } from '../services/packetService';
import { packetStore, usePacketStore } from '../store/packetStore';
import type { PacketPdfGenerateResponse } from '../types/packet';

export default function PdfPreviewScreen() {
  const { activePacket } = usePacketStore();
  const [pdfResult, setPdfResult] = useState<PacketPdfGenerateResponse | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);

  async function handleGeneratePdf() {
    if (!activePacket) {
      return;
    }

    setIsGenerating(true);
    setGenerationError(null);

    try {
      const response = await packetService.generatePdf(activePacket.id);
      setPdfResult(response);
      packetStore.updateActivePacket({ status: response.status === 'ready' ? 'ready' : 'generating_pdf' });
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
            : `Generate the final packet PDF once validation is complete for ${activePacket.offender_name}.`
        }
      />

      <View style={styles.panel}>
        <Text style={styles.sectionTitle}>Export Status</Text>
        <Text style={styles.metaText}>Packet ID: {activePacket.id.slice(0, 8)}</Text>
        <Text style={styles.metaText}>Offender: {activePacket.offender_name}</Text>
        <Text style={styles.metaText}>Packet status: {pdfResult?.status ?? activePacket.status}</Text>
        {pdfResult?.generated_at ? <Text style={styles.metaText}>Generated at: {pdfResult.generated_at}</Text> : null}
        <Pressable style={[styles.primaryButton, isGenerating && styles.primaryButtonDisabled]} onPress={handleGeneratePdf} disabled={isGenerating}>
          <Text style={styles.primaryButtonText}>{isGenerating ? 'Generating PDF…' : pdfResult ? 'Generate Again' : 'Generate Final PDF'}</Text>
        </Pressable>
        {isGenerating ? <LoadingState label="Generating final packet PDF…" /> : null}
        {generationError ? <ErrorState message={generationError} /> : null}
      </View>

      <View style={styles.panel}>
        <Text style={styles.sectionTitle}>What happens next</Text>
        {pdfResult?.status === 'ready' ? (
          <View style={styles.successState}>
            <Text style={styles.successTitle}>PDF ready</Text>
            <Text style={styles.successMessage}>The backend returned a ready PDF artifact for this packet.</Text>
            <Text style={styles.urlLabel}>PDF URL</Text>
            <Text selectable style={styles.urlValue}>{pdfResult.pdf_url}</Text>
          </View>
        ) : (
          <View style={styles.messageList}>
            <View style={styles.hintItem}>
              <Text style={styles.hintBullet}>•</Text>
              <Text style={styles.hintText}>Start generation only after the review screen shows the packet is ready for PDF.</Text>
            </View>
            <View style={styles.hintItem}>
              <Text style={styles.hintBullet}>•</Text>
              <Text style={styles.hintText}>If generation fails, go back to review and resolve any remaining validation blockers first.</Text>
            </View>
          </View>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 16 },
  centeredContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24, gap: 12 },
  title: { fontSize: 28, fontWeight: '700' },
  body: { textAlign: 'center', color: '#4b5563', fontSize: 16 },
  panel: { backgroundColor: '#ffffff', borderRadius: 12, padding: 16, borderWidth: 1, borderColor: '#e5e7eb', gap: 12 },
  sectionTitle: { fontSize: 18, fontWeight: '700', color: '#111827' },
  metaText: { color: '#111827' },
  primaryButton: { alignItems: 'center', paddingVertical: 14, borderRadius: 12, backgroundColor: '#111827' },
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
