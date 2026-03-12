import { useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import { ApiClientError } from '../services/apiClient';
import { authService } from '../services/authService';
import type { AppStackParamList } from '../navigation/AppNavigator';

export default function LoginScreen({ navigation }: NativeStackScreenProps<AppStackParamList, 'Login'>) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleLogin() {
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      await authService.login({ email, password });
    } catch (error) {
      if (error instanceof ApiClientError) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage('Unable to sign in right now.');
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Beacon</Text>
      <Text style={styles.subtitle}>Sign in to continue building a parole packet.</Text>
      <TextInput style={styles.input} autoCapitalize="none" keyboardType="email-address" placeholder="Email" value={email} onChangeText={setEmail} />
      <TextInput style={styles.input} secureTextEntry placeholder="Password" value={password} onChangeText={setPassword} />
      {errorMessage ? <Text style={styles.error}>{errorMessage}</Text> : null}
      <Pressable style={[styles.button, isSubmitting && styles.buttonDisabled]} onPress={handleLogin} disabled={isSubmitting}>
        {isSubmitting ? <ActivityIndicator color="#ffffff" /> : <Text style={styles.buttonText}>Sign In</Text>}
      </Pressable>
      <Pressable onPress={() => navigation.navigate('Register')}>
        <Text style={styles.link}>Need an account? Create one</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 24, gap: 12, backgroundColor: '#f5f7fb' },
  title: { fontSize: 32, fontWeight: '700', color: '#111827' },
  subtitle: { fontSize: 16, color: '#4b5563', marginBottom: 8 },
  input: { backgroundColor: '#ffffff', borderWidth: 1, borderColor: '#d1d5db', borderRadius: 12, paddingHorizontal: 14, paddingVertical: 12, fontSize: 16 },
  button: { backgroundColor: '#111827', borderRadius: 12, paddingVertical: 14, alignItems: 'center', marginTop: 8 },
  buttonDisabled: { opacity: 0.7 },
  buttonText: { color: '#ffffff', fontWeight: '600', fontSize: 16 },
  link: { color: '#2563eb', textAlign: 'center', fontWeight: '600', marginTop: 8 },
  error: { color: '#b91c1c', fontSize: 14 },
});
