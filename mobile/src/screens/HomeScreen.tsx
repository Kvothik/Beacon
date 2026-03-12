import { Pressable, ScrollView, StyleSheet, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import ProgressBanner from '../components/ProgressBanner';
import SectionCard from '../components/SectionCard';
import type { AppStackParamList } from '../navigation/AppNavigator';

export default function HomeScreen({ navigation }: NativeStackScreenProps<AppStackParamList, 'Home'>) {
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <ProgressBanner title="Beacon Mobile Shell" message="Navigation and placeholder screens are wired. Feature logic is intentionally not implemented yet." />
      <View style={styles.list}>
        <SectionCard title="Packet Builder" description="Placeholder packet builder shell" onPress={() => navigation.navigate('PacketBuilder')} />
        <SectionCard title="Scanner" description="Placeholder scanner shell" onPress={() => navigation.navigate('Scanner')} />
        <SectionCard title="Review" description="Placeholder review shell" onPress={() => navigation.navigate('Review')} />
        <SectionCard title="PDF Preview" description="Placeholder PDF preview shell" onPress={() => navigation.navigate('PdfPreview')} />
      </View>
      <Pressable style={styles.button} onPress={() => navigation.navigate('Login')}>
        <View>
          <SectionCard title="Back to Login" description="Return to the shell login screen" />
        </View>
      </Pressable>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 16 },
  list: { gap: 12 },
  button: { borderRadius: 12 },
});
