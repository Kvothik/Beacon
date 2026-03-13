import { useMemo, useRef, useState } from 'react';
import { Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';
import ProgressBanner from '../components/ProgressBanner';
import type { AppStackParamList } from '../navigation/AppNavigator';
import { packetService } from '../services/packetService';
import { packetStore, usePacketStore } from '../store/packetStore';
import { logWorkflowEvent } from '../utils/eventLogger';

type CapturedScan = {
  uri: string;
  width: number;
  height: number;
};

export default function ScannerScreen({ route, navigation }: NativeStackScreenProps<AppStackParamList, 'Scanner'>) {
  const { activePacket } = usePacketStore();
  const [permission, requestPermission] = useCameraPermissions();
  const cameraRef = useRef<CameraView | null>(null);
  const [capturedScan, setCapturedScan] = useState<CapturedScan | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [scanError, setScanError] = useState<string | null>(null);
  const [scanSuccess, setScanSuccess] = useState<string | null>(null);

  const qualityAssessment = useMemo(() => assessScanQuality(capturedScan), [capturedScan]);

  async function handleCapture() {
    setScanError(null);
    setScanSuccess(null);
    try {
      const photo = await cameraRef.current?.takePictureAsync({ quality: 1, imageType: 'jpg' as never });
      if (photo?.uri) {
        const captured = {
          uri: photo.uri,
          width: photo.width ?? 0,
          height: photo.height ?? 0,
        };
        setCapturedScan(captured);
        logWorkflowEvent({
          type: 'scan_captured',
          packetId: activePacket?.id,
          sectionKey: route.params.sectionKey,
          metadata: { width: captured.width, height: captured.height },
        });
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unable to capture a scan right now.';
      logWorkflowEvent({
        type: 'workflow_error',
        packetId: activePacket?.id,
        sectionKey: route.params.sectionKey,
        metadata: { source: 'scanner_capture', message },
      });
      setScanError(message);
    }
  }

  async function handleAccept() {
    if (!activePacket || !capturedScan) {
      return;
    }

    setIsUploading(true);
    setScanError(null);
    setScanSuccess(null);

    try {
      logWorkflowEvent({
        type: 'scan_accepted',
        packetId: activePacket.id,
        sectionKey: route.params.sectionKey,
        metadata: { width: capturedScan.width, height: capturedScan.height },
      });
      const upload = await packetService.createUpload(activePacket.id, {
        section_key: route.params.sectionKey,
        filename: `scan-${Date.now()}.jpg`,
        content_type: 'image/jpeg',
        source: 'scanner',
      });
      packetStore.incrementSectionDocumentCount(route.params.sectionKey);
      packetStore.addRecentDocument({
        id: upload.document_id,
        section_key: route.params.sectionKey,
        filename: upload.filename,
        source: 'scanner',
        status: 'queued',
        created_at: upload.created_at,
      });
      logWorkflowEvent({
        type: 'document_attached_to_section',
        packetId: activePacket.id,
        sectionKey: route.params.sectionKey,
        metadata: { filename: upload.filename, source: 'scanner', documentId: upload.document_id },
      });
      setScanSuccess(`Scan queued for upload as ${upload.filename}.`);
      setCapturedScan(null);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unable to queue this scan right now.';
      logWorkflowEvent({
        type: 'workflow_error',
        packetId: activePacket.id,
        sectionKey: route.params.sectionKey,
        metadata: { source: 'scanner_upload', message },
      });
      setScanError(message);
    } finally {
      setIsUploading(false);
    }
  }

  if (!activePacket) {
    return (
      <View style={styles.centeredContainer}>
        <Text style={styles.title}>Scanner</Text>
        <Text style={styles.body}>Create a packet and open the scanner from a packet section first.</Text>
      </View>
    );
  }

  if (!permission) {
    return <LoadingState label="Checking camera permission…" />;
  }

  if (!permission.granted) {
    return (
      <View style={styles.centeredContainer}>
        <Text style={styles.title}>Camera access needed</Text>
        <Text style={styles.body}>Scanner v1 needs camera permission to capture a document page.</Text>
        <Pressable style={styles.primaryButton} onPress={requestPermission}>
          <Text style={styles.primaryButtonText}>Allow Camera</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ProgressBanner
        title="Scanner"
        message={capturedScan ? 'Review the captured page, scan checks, and any rescan guidance before accepting it.' : 'Capture a document page for the selected packet section.'}
      />

      {capturedScan ? (
        <View style={styles.previewPanel}>
          <Image source={{ uri: capturedScan.uri }} style={styles.previewImage} />
          <View style={[styles.qualityPanel, qualityAssessment.shouldRescan && styles.qualityPanelWarning]}>
            <Text style={styles.qualityTitle}>{qualityAssessment.shouldRescan ? 'Rescan recommended' : 'Scan looks usable'}</Text>
            <Text style={styles.qualitySummary}>{qualityAssessment.summary}</Text>
            {qualityAssessment.recommendations.map((item) => (
              <Text key={item} style={styles.qualityItem}>• {item}</Text>
            ))}
          </View>
          <View style={styles.actionRow}>
            <Pressable
              style={styles.secondaryButton}
              onPress={() => {
                logWorkflowEvent({
                  type: 'scan_rescan_requested',
                  packetId: activePacket?.id,
                  sectionKey: route.params.sectionKey,
                  metadata: { shouldRescan: qualityAssessment.shouldRescan },
                });
                setCapturedScan(null);
              }}
            >
              <Text style={styles.secondaryButtonText}>{qualityAssessment.shouldRescan ? 'Rescan Page' : 'Retake'}</Text>
            </Pressable>
            <Pressable style={[styles.primaryButton, isUploading && styles.buttonDisabled]} onPress={handleAccept} disabled={isUploading}>
              <Text style={styles.primaryButtonText}>{isUploading ? 'Uploading…' : 'Accept Scan'}</Text>
            </Pressable>
          </View>
        </View>
      ) : (
        <View style={styles.cameraPanel}>
          <CameraView ref={cameraRef} style={styles.camera} facing="back" />
          <Text style={styles.helperText}>Prefer portrait, flat, well-lit captures for printed documents.</Text>
          <Pressable style={styles.primaryButton} onPress={handleCapture}>
            <Text style={styles.primaryButtonText}>Capture Page</Text>
          </Pressable>
        </View>
      )}

      <Pressable style={styles.secondaryButton} onPress={() => navigation.goBack()}>
        <Text style={styles.secondaryButtonText}>Back to Section</Text>
      </Pressable>

      {scanError ? <ErrorState message={scanError} /> : null}
      {scanError ? (
        <View style={styles.errorActionRow}>
          <Pressable
            style={styles.secondaryButton}
            onPress={() => {
              setScanError(null);
              if (capturedScan) {
                setCapturedScan(null);
              } else {
                handleCapture().catch(() => {
                  // state handled inside action
                });
              }
            }}
          >
            <Text style={styles.secondaryButtonText}>{capturedScan ? 'Retry Scan' : 'Retry Camera'}</Text>
          </Pressable>
          <Pressable style={styles.secondaryButton} onPress={() => navigation.goBack()}>
            <Text style={styles.secondaryButtonText}>Cancel and Return</Text>
          </Pressable>
        </View>
      ) : null}
      {scanSuccess ? <Text style={styles.successText}>{scanSuccess}</Text> : null}
    </View>
  );
}

function assessScanQuality(capturedScan: CapturedScan | null) {
  if (!capturedScan) {
    return {
      shouldRescan: false,
      summary: 'Capture a page first to see scan guidance.',
      recommendations: [] as string[],
    };
  }

  const recommendations: string[] = [];
  const portraitRatio = capturedScan.width > 0 && capturedScan.height > 0 ? capturedScan.width / capturedScan.height : 0;

  if (capturedScan.width < 1200 || capturedScan.height < 1600) {
    recommendations.push('This capture is relatively low resolution. Move closer and fill more of the frame with the page.');
  }

  if (capturedScan.width > capturedScan.height) {
    recommendations.push('The page was captured in landscape. Retake in portrait if the document is a standard vertical sheet.');
  }

  if (portraitRatio > 0 && (portraitRatio < 0.55 || portraitRatio > 0.85)) {
    recommendations.push('The page framing looks unusual for a paper document. Check for bad cropping or missing page edges.');
  }

  if (recommendations.length === 0) {
    recommendations.push('Preview the page for readability before accepting it. Retake if text looks blurry or page edges are cut off.');
  }

  return {
    shouldRescan: recommendations.some((item) => !item.startsWith('Preview the page')),
    summary:
      recommendations.length > 1 || !recommendations[0].startsWith('Preview the page')
        ? 'The scanner found conditions that may make this page harder to read in the final packet.'
        : 'No obvious framing issues were detected from the captured image dimensions.',
    recommendations,
  };
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, gap: 16, backgroundColor: '#f5f7fb' },
  centeredContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24, gap: 12 },
  title: { fontSize: 28, fontWeight: '700' },
  body: { textAlign: 'center', color: '#4b5563', fontSize: 16 },
  cameraPanel: { backgroundColor: '#ffffff', borderRadius: 12, padding: 16, gap: 12, borderWidth: 1, borderColor: '#e5e7eb' },
  previewPanel: { backgroundColor: '#ffffff', borderRadius: 12, padding: 16, gap: 12, borderWidth: 1, borderColor: '#e5e7eb' },
  camera: { height: 420, borderRadius: 12, overflow: 'hidden' },
  previewImage: { width: '100%', height: 420, borderRadius: 12, resizeMode: 'contain', backgroundColor: '#111827' },
  qualityPanel: { backgroundColor: '#ecfdf5', borderRadius: 12, borderWidth: 1, borderColor: '#a7f3d0', padding: 12, gap: 6 },
  qualityPanelWarning: { backgroundColor: '#fffbeb', borderColor: '#fcd34d' },
  qualityTitle: { color: '#111827', fontWeight: '700' },
  qualitySummary: { color: '#374151', lineHeight: 20 },
  qualityItem: { color: '#374151', lineHeight: 20 },
  helperText: { color: '#4b5563' },
  actionRow: { flexDirection: 'row', gap: 12 },
  errorActionRow: { flexDirection: 'row', gap: 12 },
  primaryButton: { alignItems: 'center', justifyContent: 'center', paddingVertical: 14, paddingHorizontal: 16, borderRadius: 12, backgroundColor: '#111827', flex: 1 },
  secondaryButton: { alignItems: 'center', justifyContent: 'center', paddingVertical: 14, paddingHorizontal: 16, borderRadius: 12, borderWidth: 1, borderColor: '#d1d5db', backgroundColor: '#ffffff' },
  primaryButtonText: { color: '#ffffff', fontWeight: '700' },
  secondaryButtonText: { color: '#111827', fontWeight: '700' },
  buttonDisabled: { opacity: 0.6 },
  successText: { color: '#166534', fontWeight: '600' },
});
