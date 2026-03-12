import { StyleSheet, Text, View } from 'react-native';

export default function PdfPreviewScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>PDF Preview</Text>
      <Text style={styles.body}>PDF preview shell only. No PDF generation or rendering logic is implemented in this issue.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24, gap: 12 },
  title: { fontSize: 28, fontWeight: '700' },
  body: { textAlign: 'center', color: '#4b5563', fontSize: 16 },
});
