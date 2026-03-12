import { Pressable, StyleSheet, Text, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import type { AppStackParamList } from '../navigation/AppNavigator';

export default function LoginScreen({ navigation }: NativeStackScreenProps<AppStackParamList, 'Login'>) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Beacon</Text>
      <Text style={styles.body}>Mobile app shell scaffolded. Authentication flow is not implemented yet.</Text>
      <Pressable style={styles.button} onPress={() => navigation.navigate('Register')}>
        <Text style={styles.buttonText}>Go to Register</Text>
      </Pressable>
      <Pressable style={styles.secondaryButton} onPress={() => navigation.navigate('Home')}>
        <Text style={styles.secondaryButtonText}>Open Shell Home</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24, gap: 16 },
  title: { fontSize: 32, fontWeight: '700' },
  body: { fontSize: 16, textAlign: 'center', color: '#4b5563' },
  button: { backgroundColor: '#111827', paddingHorizontal: 18, paddingVertical: 12, borderRadius: 10 },
  buttonText: { color: '#ffffff', fontWeight: '600' },
  secondaryButton: { paddingHorizontal: 18, paddingVertical: 12, borderRadius: 10, borderWidth: 1, borderColor: '#d1d5db' },
  secondaryButtonText: { color: '#111827', fontWeight: '600' },
});
