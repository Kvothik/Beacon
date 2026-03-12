import { useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import ProgressBanner from '../components/ProgressBanner';
import SectionCard from '../components/SectionCard';
import { authService } from '../services/authService';
import type { AppStackParamList } from '../navigation/AppNavigator';
import { useAuthStore } from '../store/authStore';

export default function HomeScreen({ navigation }: NativeStackScreenProps<AppStackParamList, 'Home'>) {
  const { session } = useAuthStore();
  const [isSigningOut, setIsSigningOut] = useState(false);

  async function handleSignOut() {
    setIsSigningOut(true);
    try {
      await authService.logout();
    } finally {
      setIsSigningOut(false);
    }
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <ProgressBanner
        title="Beacon"
        message={session ? `Signed in as ${session.user.full_name}.` : 'Authenticated mobile shell is ready.'}
      />
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

const styles = StyleSheet.create({
  container: { padding: 16, gap: 16 },
  list: { gap: 12 },
  signOutButton: { alignItems: 'center', paddingVertical: 14, borderRadius: 12, borderWidth: 1, borderColor: '#d1d5db', backgroundColor: '#ffffff' },
  signOutText: { color: '#111827', fontWeight: '600' },
});
