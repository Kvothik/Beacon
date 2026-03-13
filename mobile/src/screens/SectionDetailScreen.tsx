import { useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Switch, Text, TextInput, View } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';
import ProgressBanner from '../components/ProgressBanner';
import type { AppStackParamList } from '../navigation/AppNavigator';
import { packetService } from '../services/packetService';
import { packetStore, usePacketStore } from '../store/packetStore';
import { logWorkflowEvent } from '../utils/eventLogger';

export default function SectionDetailScreen({ route, navigation }: NativeStackScreenProps<AppStackParamList, 'SectionDetail'>) {
  const { activePacket, sections, recentDocuments } = usePacketStore();
  const section = useMemo(
    () => sections.find((candidate) => candidate.section_key === route.params.sectionKey) ?? null,
    [route.params.sectionKey, sections],
  );
  const [notesText, setNotesText] = useState(section?.notes_text ?? '');
  const [isPopulated, setIsPopulated] = useState(section?.is_populated ?? false);
  const [isSaving, setIsSaving] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const visibleDocuments = useMemo(
    () => recentDocuments.filter((document) => document.section_key === route.params.sectionKey),
    [recentDocuments, route.params.sectionKey],
  );

  async function handleSave() {
    if (!activePacket || !section) {
      return;
    }

    setIsSaving(true);
    setSaveError(null);
    setSaveSuccess(null);

    try {
      const updated = await packetService.updateSection(activePacket.id, section.section_key, {
        notes_text: notesText,
        is_populated: isPopulated,
      });
      packetStore.updateSection(section.section_key, {
        notes_text: updated.notes_text,
        is_populated: updated.is_populated,
        document_count: updated.document_count,
      });
      setSaveSuccess('Section saved.');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unable to save this section right now.';
      logWorkflowEvent({
        type: 'workflow_error',
        packetId: activePacket.id,
        sectionKey: section.section_key,
        metadata: { source: 'section_save', message },
      });
      setSaveError(message);
    } finally {
      setIsSaving(false);
    }
  }

  async function handleSelectDocument() {
    if (!activePacket || !section) {
      return;
    }

    setIsUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    try {
      const result = await DocumentPicker.getDocumentAsync({ multiple: false, copyToCacheDirectory: true });
      if (result.canceled || result.assets.length === 0) {
        setIsUploading(false);
        return;
      }

      const file = result.assets[0];
      const upload = await packetService.createUpload(activePacket.id, {
        section_key: section.section_key,
        filename: file.name,
        content_type: file.mimeType ?? 'application/octet-stream',
        source: 'upload',
      });
      packetStore.incrementSectionDocumentCount(section.section_key);
      packetStore.addRecentDocument({
        id: upload.document_id,
        section_key: section.section_key,
        filename: upload.filename,
        source: 'upload',
        status: 'queued',
        created_at: upload.created_at,
      });
      logWorkflowEvent({
        type: 'document_uploaded',
        packetId: activePacket.id,
        sectionKey: section.section_key,
        metadata: { filename: upload.filename, documentId: upload.document_id, contentType: upload.content_type },
      });
      logWorkflowEvent({
        type: 'document_attached_to_section',
        packetId: activePacket.id,
        sectionKey: section.section_key,
        metadata: { filename: upload.filename, source: 'upload', documentId: upload.document_id },
      });
      setUploadSuccess(`Upload queued for ${file.name}.`);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unable to queue this upload right now.';
      logWorkflowEvent({
        type: 'workflow_error',
        packetId: activePacket.id,
        sectionKey: section.section_key,
        metadata: { source: 'document_upload', message },
      });
      setUploadError(message);
    } finally {
      setIsUploading(false);
    }
  }

  if (!activePacket || !section) {
    return (
      <View style={styles.centeredContainer}>
        <Text style={styles.title}>Section Detail</Text>
        <Text style={styles.body}>Create a packet and open a section from the packet builder first.</Text>
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <ProgressBanner
        title={section.title}
        message={`Edit section notes, completion state, and upload supporting files for packet ${activePacket.id.slice(0, 8)}.`}
      />

      <View style={styles.panel}>
        <Text style={styles.label}>Completion</Text>
        <View style={styles.toggleRow}>
          <Text style={styles.toggleText}>{isPopulated ? 'Marked complete' : 'Not started'}</Text>
          <Switch value={isPopulated} onValueChange={setIsPopulated} />
        </View>
        <Text style={styles.metaText}>Documents queued: {section.document_count}</Text>
      </View>

      <View style={styles.panel}>
        <Text style={styles.label}>Notes</Text>
        <TextInput
          style={styles.notesInput}
          multiline
          value={notesText}
          onChangeText={setNotesText}
          placeholder="Add section-specific notes here"
          textAlignVertical="top"
        />
      </View>

      <Pressable style={[styles.primaryButton, isSaving && styles.primaryButtonDisabled]} onPress={handleSave} disabled={isSaving}>
        <Text style={styles.primaryButtonText}>{isSaving ? 'Saving…' : 'Save Section'}</Text>
      </Pressable>

      <Pressable style={[styles.secondaryButton, isUploading && styles.primaryButtonDisabled]} onPress={handleSelectDocument} disabled={isUploading}>
        <Text style={styles.secondaryButtonText}>{isUploading ? 'Selecting…' : 'Select Document'}</Text>
      </Pressable>

      <Pressable style={styles.secondaryButton} onPress={() => navigation.navigate('Scanner', { sectionKey: section.section_key })}>
        <Text style={styles.secondaryButtonText}>Scan Document</Text>
      </Pressable>

      <View style={styles.panel}>
        <Text style={styles.label}>Recent Attachments</Text>
        <Text style={styles.metaText}>Use this list to verify which document was just attached to this section.</Text>
        {visibleDocuments.length === 0 ? <Text style={styles.metaText}>No visible attachments yet for this section.</Text> : null}
        {visibleDocuments.map((document) => (
          <View key={document.id} style={styles.documentRow}>
            <Text style={styles.documentTitle}>{document.filename}</Text>
            <Text style={styles.documentMeta}>{document.source === 'scanner' ? 'Scanned document' : 'Uploaded document'} • {document.status}</Text>
          </View>
        ))}
      </View>

      {isSaving ? <LoadingState label="Saving section to the backend…" /> : null}
      {isUploading ? <LoadingState label="Selecting document and creating upload…" /> : null}
      {saveError ? <ErrorState message={saveError} /> : null}
      {saveError ? (
        <View style={styles.errorActionRow}>
          <Pressable style={styles.secondaryButton} onPress={() => handleSave().catch(() => {})}>
            <Text style={styles.secondaryButtonText}>Retry Save</Text>
          </Pressable>
          <Pressable style={styles.secondaryButton} onPress={() => navigation.navigate('PacketBuilder')}>
            <Text style={styles.secondaryButtonText}>Cancel and Return</Text>
          </Pressable>
        </View>
      ) : null}
      {uploadError ? <ErrorState message={uploadError} /> : null}
      {uploadError ? (
        <View style={styles.errorActionRow}>
          <Pressable style={styles.secondaryButton} onPress={() => handleSelectDocument().catch(() => {})}>
            <Text style={styles.secondaryButtonText}>Retry Upload</Text>
          </Pressable>
          <Pressable style={styles.secondaryButton} onPress={() => navigation.navigate('PacketBuilder')}>
            <Text style={styles.secondaryButtonText}>Cancel and Return</Text>
          </Pressable>
        </View>
      ) : null}
      {saveSuccess ? <Text style={styles.successText}>{saveSuccess}</Text> : null}
      {uploadSuccess ? <Text style={styles.successText}>{uploadSuccess}</Text> : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 16 },
  centeredContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24, gap: 12 },
  panel: { backgroundColor: '#ffffff', borderRadius: 12, padding: 16, borderWidth: 1, borderColor: '#e5e7eb', gap: 12 },
  title: { fontSize: 28, fontWeight: '700' },
  body: { textAlign: 'center', color: '#4b5563', fontSize: 16 },
  label: { fontSize: 16, fontWeight: '700', color: '#111827' },
  toggleRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 12 },
  toggleText: { color: '#111827' },
  metaText: { color: '#4b5563' },
  notesInput: { minHeight: 180, borderWidth: 1, borderColor: '#d1d5db', borderRadius: 12, padding: 12, backgroundColor: '#ffffff', color: '#111827' },
  primaryButton: { alignItems: 'center', paddingVertical: 14, borderRadius: 12, backgroundColor: '#111827' },
  secondaryButton: { alignItems: 'center', paddingVertical: 14, borderRadius: 12, borderWidth: 1, borderColor: '#d1d5db', backgroundColor: '#ffffff' },
  errorActionRow: { flexDirection: 'row', gap: 12 },
  primaryButtonDisabled: { opacity: 0.6 },
  primaryButtonText: { color: '#ffffff', fontWeight: '700' },
  secondaryButtonText: { color: '#111827', fontWeight: '700' },
  documentRow: { backgroundColor: '#f9fafb', borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 12, padding: 12, gap: 4 },
  documentTitle: { color: '#111827', fontWeight: '600' },
  documentMeta: { color: '#4b5563', fontSize: 13 },
  successText: { color: '#166534', fontWeight: '600' },
});
