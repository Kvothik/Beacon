import { StyleSheet, Text, View } from 'react-native';

type Props = {
  title: string;
  description: string;
};

export default function DocumentUploader({ title, description }: Props) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.description}>{description}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { backgroundColor: '#ffffff', borderRadius: 12, padding: 16, borderWidth: 1, borderColor: '#e5e7eb', gap: 6 },
  title: { fontSize: 16, fontWeight: '600', color: '#111827' },
  description: { fontSize: 14, color: '#4b5563' },
});
