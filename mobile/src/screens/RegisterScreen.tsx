import { useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import { ApiClientError } from '../services/apiClient';
import { authService } from '../services/authService';
import type { AppStackParamList } from '../navigation/AppNavigator';

export default function RegisterScreen({ navigation }: NativeStackScreenProps<AppStackParamList, 'Register'>) {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleRegister() {
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      await authService.register({ full_name: fullName, email, password });
    } catch (error) {
      if (error instanceof ApiClientError) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage('Unable to create your account right now.');
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Create Account</Text>
      <Text style={styles.subtitle}>Start with a saved Beacon account.</Text>
      <TextInput style={styles.input} placeholder="Full name" value={fullName} onChangeText={setFullName} />
      <TextInput style={styles.input} autoCapitalize="none" keyboardType="email-address" placeholder="Email" value={email} onChangeText={setEmail} />
      <TextInput style={styles.input} secureTextEntry placeholder="Password" value={password} onChangeText={setPassword} />
      {errorMessage ? <Text style={styles.error}>{errorMessage}</Text> : null}
      <Pressable style={[styles.button, isSubmitting && styles.buttonDisabled]} onPress={handleRegister} disabled={isSubmitting}>
        {isSubmitting ? <ActivityIndicator color="#ffffff" /> : <Text style={styles.buttonText}>Create Account</Text>}
      </Pressable>
      <Pressable onPress={() => navigation.navigate('Login')}>
        <Text style={styles.link}>Already have an account? Sign in</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 24, gap: 12, backgroundColor: '#f5f7fb' },
  title: { fontSize: 30, fontWeight: '700', color: '#111827' },
  subtitle: { fontSize: 16, color: '#4b5563', marginBottom: 8 },
  input: { backgroundColor: '#ffffff', borderWidth: 1, borderColor: '#d1d5db', borderRadius: 12, paddingHorizontal: 14, paddingVertical: 12, fontSize: 16 },
  button: { backgroundColor: '#111827', borderRadius: 12, paddingVertical: 14, alignItems: 'center', marginTop: 8 },
  buttonDisabled: { opacity: 0.7 },
  buttonText: { color: '#ffffff', fontWeight: '600', fontSize: 16 },
  link: { color: '#2563eb', textAlign: 'center', fontWeight: '600', marginTop: 8 },
  error: { color: '#b91c1c', fontSize: 14 },
});
