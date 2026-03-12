import { useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';
import ProgressBanner from '../components/ProgressBanner';
import SectionCard from '../components/SectionCard';
import { authService } from '../services/authService';
import { offenderService } from '../services/offenderService';
import type { AppStackParamList } from '../navigation/AppNavigator';
import { useAuthStore } from '../store/authStore';
import { offenderStore, useOffenderStore } from '../store/offenderStore';
import type { OffenderSummary } from '../types/offender';

export default function HomeScreen({ navigation }: NativeStackScreenProps<AppStackParamList, 'Home'>) {
  const { session } = useAuthStore();
  const { results, pagination, selectedOffenderSid, selectedOffenderDetail } = useOffenderStore();
  const [isSigningOut, setIsSigningOut] = useState(false);
  const [lastName, setLastName] = useState('');
  const [firstNameInitial, setFirstNameInitial] = useState('');
  const [tdcjNumber, setTdcjNumber] = useState('');
  const [sid, setSid] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const selectedSummary = useMemo(
    () => results.find((result) => result.sid === selectedOffenderSid) ?? null,
    [results, selectedOffenderSid],
  );

  async function handleSignOut() {
    setIsSigningOut(true);
    try {
      offenderStore.reset();
      await authService.logout();
    } finally {
      setIsSigningOut(false);
    }
  }

  async function handleSearch() {
    setIsSearching(true);
    setHasSearched(true);
    setSearchError(null);
    setDetailError(null);

    try {
      const response = await offenderService.search({
        last_name: lastName,
        first_name_initial: firstNameInitial,
        tdcj_number: tdcjNumber,
        sid,
        page: 1,
      });
      offenderStore.setSearchResults(response.results, response.pagination);
    } catch (error) {
      offenderStore.reset();
      setSearchError(error instanceof Error ? error.message : 'Unable to search for offenders right now.');
    } finally {
      setIsSearching(false);
    }
  }

  async function handleSelectOffender(offender: OffenderSummary) {
    setIsLoadingDetail(true);
    setDetailError(null);
    offenderStore.setSelectedOffenderSid(offender.sid);

    try {
      const detail = await offenderService.getDetail(offender.sid);
      offenderStore.setSelectedOffenderDetail(detail);
    } catch (error) {
      offenderStore.setSelectedOffenderDetail(null);
      setDetailError(error instanceof Error ? error.message : 'Unable to load offender details right now.');
    } finally {
      setIsLoadingDetail(false);
    }
  }

  const canSearch = !isSearching && Boolean((lastName.trim() && firstNameInitial.trim()) || tdcjNumber.trim() || sid.trim());

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <ProgressBanner
        title="Beacon"
        message={session ? `Signed in as ${session.user.full_name}. Search for an offender to begin the guided parole packet flow.` : 'Authenticated mobile shell is ready.'}
      />

      <View style={styles.panel}>
        <Text style={styles.sectionTitle}>Offender Lookup</Text>
        <Text style={styles.sectionDescription}>Search by last name + first initial, TDCJ number, or SID. Results come from the backend lookup API.</Text>
        <TextInput style={styles.input} placeholder="Last name" value={lastName} onChangeText={setLastName} autoCapitalize="words" />
        <TextInput style={styles.input} placeholder="First initial" value={firstNameInitial} onChangeText={(value) => setFirstNameInitial(value.slice(0, 1))} autoCapitalize="characters" />
        <Text style={styles.orText}>or</Text>
        <TextInput style={styles.input} placeholder="TDCJ number" value={tdcjNumber} onChangeText={setTdcjNumber} autoCapitalize="characters" />
        <TextInput style={styles.input} placeholder="SID" value={sid} onChangeText={setSid} autoCapitalize="characters" />
        <Pressable style={[styles.primaryButton, !canSearch && styles.primaryButtonDisabled]} onPress={handleSearch} disabled={!canSearch}>
          <Text style={styles.primaryButtonText}>{isSearching ? 'Searching…' : 'Search Offenders'}</Text>
        </Pressable>
        {isSearching ? <LoadingState label="Searching TDCJ through the backend…" /> : null}
        {searchError ? <ErrorState message={searchError} /> : null}
        {hasSearched && !isSearching && !searchError && results.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>No matching offenders found</Text>
            <Text style={styles.emptyMessage}>Try another search mode or double-check the entered values.</Text>
          </View>
        ) : null}
      </View>

      {results.length > 0 ? (
        <View style={styles.panel}>
          <Text style={styles.sectionTitle}>Search Results</Text>
          <Text style={styles.sectionDescription}>
            {pagination ? `Page ${pagination.current_page} of ${pagination.total_pages}` : 'Results'}
          </Text>
          <View style={styles.list}>
            {results.map((result) => (
              <SectionCard
                key={result.sid}
                title={`${result.name} (${result.sid})`}
                description={formatResultDescription(result)}
                onPress={() => handleSelectOffender(result)}
              />
            ))}
          </View>
        </View>
      ) : null}

      {selectedSummary ? (
        <View style={styles.panel}>
          <Text style={styles.sectionTitle}>Selected Offender</Text>
          <Text style={styles.sectionDescription}>Review the normalized offender detail returned from the backend before moving on to parole-board lookup and packet creation.</Text>
          <View style={styles.detailCard}>
            <Text style={styles.detailTitle}>{selectedSummary.name}</Text>
            <DetailRow label="SID" value={selectedSummary.sid} />
            <DetailRow label="TDCJ Number" value={selectedSummary.tdcj_number} />
            <DetailRow label="Current Unit" value={selectedSummary.unit} />
          </View>
          {isLoadingDetail ? <LoadingState label="Loading offender detail…" /> : null}
          {detailError ? <ErrorState message={detailError} /> : null}
          {selectedOffenderDetail ? (
            <View style={styles.detailCard}>
              <DetailRow label="Name" value={selectedOffenderDetail.name} />
              <DetailRow label="Current Facility" value={selectedOffenderDetail.current_facility} />
              <DetailRow label="Projected Release Date" value={selectedOffenderDetail.projected_release_date} />
              <DetailRow label="Parole Eligibility Date" value={selectedOffenderDetail.parole_eligibility_date} />
              <DetailRow label="Visitation Eligible" value={selectedOffenderDetail.visitation_eligible_raw} />
              <DetailRow label="Maximum Sentence Date" value={selectedOffenderDetail.maximum_sentence_date} />
              <DetailRow label="Scheduled Release Date" value={selectedOffenderDetail.scheduled_release_date_text} />
            </View>
          ) : null}
        </View>
      ) : null}

      <View style={styles.list}>
        <SectionCard title="Packet Builder" description="Placeholder packet builder shell" onPress={() => navigation.navigate('PacketBuilder')} />
        <SectionCard title="Scanner" description="Placeholder scanner shell" onPress={() => navigation.navigate('Scanner')} />
        <SectionCard title="Review" description="Placeholder review shell" onPress={() => navigation.navigate('Review')} />
        <SectionCard title="PDF Preview" description="Placeholder PDF preview shell" onPress={() => navigation.navigate('PdfPreview')} />
      </View>

      <Pressable style={styles.signOutButton} onPress={handleSignOut} disabled={isSigningOut}>
        <Text style={styles.signOutText}>{isSigningOut ? 'Signing Out…' : 'Sign Out'}</Text>
      </Pressable>
    </ScrollView>
  );
}

type DetailRowProps = {
  label: string;
  value: string | number | null | undefined;
};

function DetailRow({ label, value }: DetailRowProps) {
  return (
    <View style={styles.detailRow}>
      <Text style={styles.detailLabel}>{label}</Text>
      <Text style={styles.detailValue}>{value ?? 'Not available'}</Text>
    </View>
  );
}

function formatResultDescription(result: OffenderSummary) {
  const parts = [
    result.tdcj_number ? `TDCJ ${result.tdcj_number}` : null,
    result.unit ? `Unit ${result.unit}` : null,
    result.projected_release_date ? `Projected release ${result.projected_release_date}` : null,
  ].filter(Boolean);

  return parts.length > 0 ? parts.join(' • ') : 'Tap to load normalized offender detail.';
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 16 },
  panel: { backgroundColor: '#ffffff', borderRadius: 12, padding: 16, borderWidth: 1, borderColor: '#e5e7eb', gap: 12 },
  sectionTitle: { fontSize: 18, fontWeight: '700', color: '#111827' },
  sectionDescription: { color: '#4b5563', lineHeight: 20 },
  input: { borderWidth: 1, borderColor: '#d1d5db', borderRadius: 12, paddingHorizontal: 12, paddingVertical: 12, backgroundColor: '#ffffff', color: '#111827' },
  orText: { alignSelf: 'center', color: '#6b7280', fontWeight: '600' },
  primaryButton: { alignItems: 'center', paddingVertical: 14, borderRadius: 12, backgroundColor: '#111827' },
  primaryButtonDisabled: { opacity: 0.6 },
  primaryButtonText: { color: '#ffffff', fontWeight: '700' },
  emptyState: { backgroundColor: '#f9fafb', borderRadius: 12, padding: 16, borderWidth: 1, borderColor: '#e5e7eb', gap: 6 },
  emptyTitle: { fontSize: 16, fontWeight: '600', color: '#111827' },
  emptyMessage: { color: '#4b5563' },
  list: { gap: 12 },
  detailCard: { backgroundColor: '#f9fafb', borderRadius: 12, borderWidth: 1, borderColor: '#e5e7eb', padding: 16, gap: 10 },
  detailTitle: { fontSize: 16, fontWeight: '700', color: '#111827' },
  detailRow: { gap: 4 },
  detailLabel: { fontSize: 12, fontWeight: '700', letterSpacing: 0.4, textTransform: 'uppercase', color: '#6b7280' },
  detailValue: { fontSize: 15, color: '#111827' },
  signOutButton: { alignItems: 'center', paddingVertical: 14, borderRadius: 12, borderWidth: 1, borderColor: '#d1d5db', backgroundColor: '#ffffff' },
  signOutText: { color: '#111827', fontWeight: '600' },
});
