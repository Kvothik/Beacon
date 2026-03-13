import { useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';
import ProgressBanner from '../components/ProgressBanner';
import SectionCard from '../components/SectionCard';
import type { AppStackParamList } from '../navigation/AppNavigator';
import { authService } from '../services/authService';
import { offenderService } from '../services/offenderService';
import { packetService } from '../services/packetService';
import { useAuthStore } from '../store/authStore';
import { offenderStore, useOffenderStore } from '../store/offenderStore';
import { packetStore, usePacketStore } from '../store/packetStore';
import type { OffenderSummary } from '../types/offender';

export default function HomeScreen({ navigation }: NativeStackScreenProps<AppStackParamList, 'Home'>) {
  const { session } = useAuthStore();
  const { results, pagination, selectedOffenderSid, selectedOffenderDetail, selectedParoleBoardOffice } = useOffenderStore();
  const { activePacket } = usePacketStore();
  const [isSigningOut, setIsSigningOut] = useState(false);
  const [lastName, setLastName] = useState('');
  const [firstNameInitial, setFirstNameInitial] = useState('');
  const [tdcjNumber, setTdcjNumber] = useState('');
  const [sid, setSid] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [isLoadingParoleBoard, setIsLoadingParoleBoard] = useState(false);
  const [isCreatingPacket, setIsCreatingPacket] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [paroleBoardError, setParoleBoardError] = useState<string | null>(null);
  const [packetError, setPacketError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [resultsFilter, setResultsFilter] = useState('');
  const [showSearchResults, setShowSearchResults] = useState(true);

  const selectedSummary = useMemo(
    () => results.find((result) => result.sid === selectedOffenderSid) ?? null,
    [results, selectedOffenderSid],
  );

  const visibleResults = useMemo(() => {
    const needle = resultsFilter.trim().toUpperCase();
    const filteredResults = !needle
      ? results
      : results.filter((result) => {
          const haystack = [result.name, result.sid, result.tdcj_number, result.unit, result.projected_release_date]
            .filter(Boolean)
            .join(' ')
            .toUpperCase();
          return haystack.includes(needle);
        });

    return [...filteredResults].sort((left, right) => {
      if (left.sid === selectedOffenderSid) {
        return -1;
      }
      if (right.sid === selectedOffenderSid) {
        return 1;
      }
      return 0;
    });
  }, [results, resultsFilter, selectedOffenderSid]);

  async function handleSignOut() {
    setIsSigningOut(true);
    try {
      offenderStore.reset();
      packetStore.reset();
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
    setParoleBoardError(null);
    setPacketError(null);

    try {
      const response = await offenderService.search({
        last_name: lastName,
        first_name_initial: firstNameInitial,
        tdcj_number: tdcjNumber,
        sid,
        page: 1,
      });
      offenderStore.setSearchResults(response.results, response.pagination);
      setResultsFilter('');
      setShowSearchResults(true);
      packetStore.reset();
    } catch (error) {
      offenderStore.reset();
      packetStore.reset();
      setSearchError(error instanceof Error ? error.message : 'Unable to search for offenders right now.');
    } finally {
      setIsSearching(false);
    }
  }

  async function handleSelectOffender(offender: OffenderSummary) {
    setIsLoadingDetail(true);
    setIsLoadingParoleBoard(false);
    setDetailError(null);
    setParoleBoardError(null);
    setPacketError(null);
    offenderStore.setSelectedOffenderSid(offender.sid);
    offenderStore.setSelectedParoleBoardOffice(null);
    setShowSearchResults(false);
    packetStore.reset();

    try {
      const detail = await offenderService.getDetail(offender.sid);
      offenderStore.setSelectedOffenderDetail(detail);

      const lookupUnit = detail.current_facility ?? offender.unit;
      if (lookupUnit) {
        setIsLoadingParoleBoard(true);
        try {
          const office = await offenderService.getParoleBoardOffice(lookupUnit, offender.sid);
          offenderStore.setSelectedParoleBoardOffice(office);
        } catch (error) {
          offenderStore.setSelectedParoleBoardOffice(null);
          setParoleBoardError(error instanceof Error ? error.message : 'Unable to load parole board office information right now.');
        } finally {
          setIsLoadingParoleBoard(false);
        }
      }
    } catch (error) {
      offenderStore.setSelectedOffenderDetail(null);
      offenderStore.setSelectedParoleBoardOffice(null);
      setDetailError(error instanceof Error ? error.message : 'Unable to load offender details right now.');
    } finally {
      setIsLoadingDetail(false);
    }
  }

  async function handleCreatePacket() {
    if (!selectedOffenderDetail) {
      return;
    }

    setIsCreatingPacket(true);
    setPacketError(null);

    try {
      const packet = await packetService.create({
        offender_sid: selectedOffenderDetail.sid,
        offender_name: selectedOffenderDetail.name ?? selectedSummary?.name ?? 'Unknown Offender',
        offender_tdcj_number: selectedOffenderDetail.tdcj_number,
        current_facility: selectedOffenderDetail.current_facility,
        parole_board_office_code: selectedParoleBoardOffice?.office_code ?? null,
      });
      packetStore.setActivePacket(packet);
      navigation.navigate('PacketBuilder');
    } catch (error) {
      setPacketError(error instanceof Error ? error.message : 'Unable to create a packet right now.');
    } finally {
      setIsCreatingPacket(false);
    }
  }

  const canSearch = !isSearching && Boolean((lastName.trim() && firstNameInitial.trim()) || tdcjNumber.trim() || sid.trim());
  const canCreatePacket = Boolean(selectedOffenderDetail && selectedParoleBoardOffice && !isCreatingPacket);

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
          <View style={styles.resultsHeader}>
            <View style={styles.resultsHeaderCopy}>
              <Text style={styles.sectionTitle}>Search Results</Text>
              <Text style={styles.sectionDescription}>
                {pagination ? `Page ${pagination.current_page} of ${pagination.total_pages}` : 'Results'}
              </Text>
            </View>
            {selectedSummary ? (
              <Pressable style={styles.secondaryButton} onPress={() => setShowSearchResults((current) => !current)}>
                <Text style={styles.secondaryButtonText}>{showSearchResults ? 'Hide Results' : 'Choose Different Offender'}</Text>
              </Pressable>
            ) : null}
          </View>
          {results.length > 1 ? (
            <>
              <TextInput
                style={styles.input}
                placeholder="Filter current results by SID, TDCJ, unit, or name"
                value={resultsFilter}
                onChangeText={setResultsFilter}
                autoCapitalize="characters"
              />
              <Text style={styles.helperText}>Use SID, TDCJ number, unit, or any part of the name to narrow large result sets quickly.</Text>
            </>
          ) : null}
          {showSearchResults ? (
            visibleResults.length > 0 ? (
              <View style={styles.list}>
                {visibleResults.map((result) => {
                  const isSelected = result.sid === selectedOffenderSid;
                  return (
                    <Pressable
                      key={result.sid}
                      style={[styles.resultCard, isSelected && styles.resultCardSelected]}
                      onPress={() => handleSelectOffender(result)}
                    >
                      <View style={styles.resultCardHeader}>
                        <View style={styles.resultCardTitleRow}>
                          {isSelected ? <Text style={styles.selectedCheckmark}>✓</Text> : null}
                          <Text style={styles.resultCardTitle}>{result.name} ({result.sid})</Text>
                        </View>
                        {isSelected ? <Text style={styles.selectedBadge}>Selected</Text> : null}
                      </View>
                      <Text style={styles.resultCardDescription}>{formatResultDescription(result)}</Text>
                      {isSelected ? <Text style={styles.selectedHelper}>This is the currently selected offender for the packet flow.</Text> : null}
                    </Pressable>
                  );
                })}
              </View>
            ) : (
              <View style={styles.emptyState}>
                <Text style={styles.emptyTitle}>No filtered results match</Text>
                <Text style={styles.emptyMessage}>Clear or change the filter to see more offenders from this search.</Text>
              </View>
            )
          ) : (
            <View style={styles.emptyState}>
              <Text style={styles.emptyTitle}>Results collapsed</Text>
              <Text style={styles.emptyMessage}>The selected offender is shown below. Use “Choose Different Offender” if you need to switch.</Text>
            </View>
          )}
        </View>
      ) : null}

      {selectedSummary ? (
        <View style={styles.panel}>
          <Text style={styles.sectionTitle}>Selected Offender</Text>
          <Text style={styles.sectionDescription}>Review the normalized offender detail returned from the backend before moving on to packet creation.</Text>
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
          {isLoadingParoleBoard ? <LoadingState label="Loading parole board office…" /> : null}
          {paroleBoardError ? <ErrorState message={paroleBoardError} /> : null}
          {selectedParoleBoardOffice ? (
            <View style={styles.detailCard}>
              <Text style={styles.detailTitle}>Parole Board Office</Text>
              <DetailRow label="Office Name" value={selectedParoleBoardOffice.office_name} />
              <DetailRow label="Office Code" value={selectedParoleBoardOffice.office_code} />
              <DetailRow label="Mailing Address" value={formatMailingAddress(selectedParoleBoardOffice.address_lines)} />
              <DetailRow label="City" value={selectedParoleBoardOffice.city} />
              <DetailRow label="State" value={selectedParoleBoardOffice.state} />
              <DetailRow label="ZIP" value={selectedParoleBoardOffice.postal_code} />
              <DetailRow label="Contact Phone" value={selectedParoleBoardOffice.phone} />
            </View>
          ) : null}
          <Pressable style={[styles.primaryButton, !canCreatePacket && styles.primaryButtonDisabled]} onPress={handleCreatePacket} disabled={!canCreatePacket}>
            <Text style={styles.primaryButtonText}>{isCreatingPacket ? 'Creating Packet…' : 'Create Packet'}</Text>
          </Pressable>
          {isCreatingPacket ? <LoadingState label="Creating packet and preparing sections…" /> : null}
          {packetError ? <ErrorState message={packetError} /> : null}
        </View>
      ) : null}

      <View style={styles.list}>
        {activePacket ? <SectionCard title="Packet Builder" description="Open the active packet builder flow" onPress={() => navigation.navigate('PacketBuilder')} /> : null}
        <SectionCard title="Scanner" description="Open scanner flow (defaults to Photos section when launched from Home)" onPress={() => navigation.navigate('Scanner', { sectionKey: 'photos' })} />
        <SectionCard title="Review" description="Placeholder review shell" onPress={() => navigation.navigate('Review')} />
        <SectionCard title="PDF Export" description="Open the final packet PDF generation flow" onPress={() => navigation.navigate('PdfPreview')} />
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

function formatMailingAddress(addressLines: string[]) {
  return addressLines.join(', ');
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
  helperText: { color: '#6b7280', fontSize: 13, lineHeight: 18 },
  list: { gap: 12 },
  resultsHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', gap: 12 },
  resultsHeaderCopy: { flex: 1, gap: 4 },
  secondaryButton: { alignItems: 'center', justifyContent: 'center', paddingHorizontal: 12, paddingVertical: 10, borderRadius: 12, borderWidth: 1, borderColor: '#d1d5db', backgroundColor: '#ffffff' },
  secondaryButtonText: { color: '#111827', fontWeight: '600', fontSize: 13 },
  resultCard: { backgroundColor: '#ffffff', borderRadius: 12, padding: 16, borderWidth: 1, borderColor: '#e5e7eb', gap: 8 },
  resultCardSelected: {
    borderColor: '#2563eb',
    borderWidth: 2,
    backgroundColor: '#eff6ff',
    shadowColor: '#2563eb',
    shadowOpacity: 0.12,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
    elevation: 2,
  },
  resultCardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10 },
  resultCardTitleRow: { flex: 1, flexDirection: 'row', alignItems: 'center', gap: 8 },
  selectedCheckmark: { color: '#1d4ed8', fontWeight: '800', fontSize: 18, lineHeight: 20 },
  resultCardTitle: { flex: 1, fontSize: 16, fontWeight: '600', color: '#111827' },
  resultCardDescription: { fontSize: 14, color: '#4b5563', lineHeight: 20 },
  selectedBadge: {
    color: '#1d4ed8',
    fontWeight: '700',
    fontSize: 12,
    textTransform: 'uppercase',
    backgroundColor: '#dbeafe',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 999,
    overflow: 'hidden',
  },
  selectedHelper: { color: '#1d4ed8', fontSize: 13, fontWeight: '600' },
  detailCard: { backgroundColor: '#f9fafb', borderRadius: 12, borderWidth: 1, borderColor: '#e5e7eb', padding: 16, gap: 10 },
  detailTitle: { fontSize: 16, fontWeight: '700', color: '#111827' },
  detailRow: { gap: 4 },
  detailLabel: { fontSize: 12, fontWeight: '700', letterSpacing: 0.4, textTransform: 'uppercase', color: '#6b7280' },
  detailValue: { fontSize: 15, color: '#111827' },
  signOutButton: { alignItems: 'center', paddingVertical: 14, borderRadius: 12, borderWidth: 1, borderColor: '#d1d5db', backgroundColor: '#ffffff' },
  signOutText: { color: '#111827', fontWeight: '600' },
});
