import { ActivityIndicator, StyleSheet, Text, View } from 'react-native';

type Props = {
  label?: string;
};

export default function LoadingState({ label = 'Loading…' }: Props) {
  return (
    <View style={styles.container}>
      <ActivityIndicator size="small" color="#111827" />
      <Text style={styles.label}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  label: { fontSize: 14, color: '#4b5563' },
});
