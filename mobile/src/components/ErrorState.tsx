import { StyleSheet, Text, View } from 'react-native';

type Props = {
  message: string;
};

export default function ErrorState({ message }: Props) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Something went wrong</Text>
      <Text style={styles.message}>{message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { backgroundColor: '#fef2f2', borderColor: '#fecaca', borderWidth: 1, borderRadius: 12, padding: 16, gap: 6 },
  title: { fontSize: 16, fontWeight: '600', color: '#991b1b' },
  message: { color: '#7f1d1d' },
});
