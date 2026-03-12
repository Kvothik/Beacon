import { ScrollView, StyleSheet } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import DocumentUploader from '../components/DocumentUploader';
import ProgressBanner from '../components/ProgressBanner';
import SectionCard from '../components/SectionCard';
import type { AppStackParamList } from '../navigation/AppNavigator';

export default function PacketBuilderScreen({ navigation }: NativeStackScreenProps<AppStackParamList, 'PacketBuilder'>) {
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <ProgressBanner title="Packet Builder Shell" message="Section navigation is scaffolded; packet data and editing are not implemented in this issue." />
      <SectionCard title="Section Detail" description="Open placeholder section detail screen" onPress={() => navigation.navigate('SectionDetail')} />
      <SectionCard title="Scanner" description="Open placeholder scanner screen" onPress={() => navigation.navigate('Scanner')} />
      <DocumentUploader title="Document Uploader" description="Upload scaffold only; no file handling is implemented yet." />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 16 },
});
