import { useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Switch, Text, TextInput, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';
import ProgressBanner from '../components/ProgressBanner';
import type { AppStackParamList } from '../navigation/AppNavigator';
import { packetService } from '../services/packetService';
import { packetStore, usePacketStore } from '../store/packetStore';

export default function SectionDetailScreen({ route }: NativeStackScreenProps<AppStackParamList, 'SectionDetail'>) {
  const { activePacket, sections } = usePacketStore();
  const section = useMemo(
    () => sections.find((candidate) => candidate.section_key === route.params.sectionKey) ?? null,
    [route.params.sectionKey, sections],
  );
  const [notesText, setNotesText] = useState(section?.notes_text ?? '');
  const [isPopulated, setIsPopulated] = useState(section?.is_populated ?? false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);

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
      });
      setSaveSuccess('Section saved.')
    } catch (error) {
      setSaveError(error instanceof Error ? error.message : 'Unable to save this section right now.');
    } finally {
      setIsSaving(false);
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
        message={`Edit section notes and completion state for packet ${activePacket.id.slice(0, 8)}.`}
      />

      <View style={styles.panel}>
        <Text style={styles.label}>Completion</Text>
        <View style={styles.toggleRow}>
          <Text style={styles.toggleText}>{isPopulated ? 'Marked complete' : 'Not started'}</Text>
          <Switch value={isPopulated} onValueChange={setIsPopulated} />
        </View>
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

      {isSaving ? <LoadingState label="Saving section to the backend…" /> : null}
      {saveError ? <ErrorState message={saveError} /> : null}
      {saveSuccess ? <Text style={styles.successText}>{saveSuccess}</Text> : null}
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
  notesInput: { minHeight: 180, borderWidth: 1, borderColor: '#d1d5db', borderRadius: 12, padding: 12, backgroundColor: '#ffffff', color: '#111827' },
  primaryButton: { alignItems: 'center', paddingVertical: 14, borderRadius: 12, backgroundColor: '#111827' },
  primaryButtonDisabled: { opacity: 0.6 },
  primaryButtonText: { color: '#ffffff', fontWeight: '700' },
  successText: { color: '#166534', fontWeight: '600' },
});
