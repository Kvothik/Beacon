import { StyleSheet, Text, View } from 'react-native';

export default function SectionDetailScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Section Detail</Text>
      <Text style={styles.body}>This is a placeholder shell for packet section detail. No section-specific logic is implemented yet.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24, gap: 12 },
  title: { fontSize: 28, fontWeight: '700' },
  body: { textAlign: 'center', color: '#4b5563', fontSize: 16 },
});
