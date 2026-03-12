import { StyleSheet, Text, View } from 'react-native';

export default function ReviewScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Review</Text>
      <Text style={styles.body}>Review shell only. Packet completeness and export behavior are not implemented in this issue.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24, gap: 12 },
  title: { fontSize: 28, fontWeight: '700' },
  body: { textAlign: 'center', color: '#4b5563', fontSize: 16 },
});
