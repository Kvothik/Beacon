import { Pressable, StyleSheet, Text, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import type { AppStackParamList } from '../navigation/AppNavigator';

export default function RegisterScreen({ navigation }: NativeStackScreenProps<AppStackParamList, 'Register'>) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Create Account</Text>
      <Text style={styles.body}>Registration UI scaffold only. No form submission logic is implemented.</Text>
      <Pressable style={styles.button} onPress={() => navigation.navigate('Login')}>
        <Text style={styles.buttonText}>Back to Login</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24, gap: 16 },
  title: { fontSize: 28, fontWeight: '700' },
  body: { fontSize: 16, textAlign: 'center', color: '#4b5563' },
  button: { backgroundColor: '#111827', paddingHorizontal: 18, paddingVertical: 12, borderRadius: 10 },
  buttonText: { color: '#ffffff', fontWeight: '600' },
});
