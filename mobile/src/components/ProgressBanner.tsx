import { StyleSheet, Text, View } from 'react-native';

type Props = {
  title: string;
  message: string;
};

export default function ProgressBanner({ title, message }: Props) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.message}>{message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { backgroundColor: '#111827', borderRadius: 12, padding: 16, gap: 8 },
  title: { color: '#ffffff', fontSize: 18, fontWeight: '700' },
  message: { color: '#e5e7eb', fontSize: 14 },
});
