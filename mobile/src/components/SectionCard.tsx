import { Pressable, StyleSheet, Text, View } from 'react-native';

type Props = {
  title: string;
  description: string;
  onPress?: () => void;
};

export default function SectionCard({ title, description, onPress }: Props) {
  return (
    <Pressable style={styles.card} onPress={onPress} disabled={!onPress}>
      <View style={styles.content}>
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.description}>{description}</Text>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: '#ffffff', borderRadius: 12, padding: 16, borderWidth: 1, borderColor: '#e5e7eb' },
  content: { gap: 6 },
  title: { fontSize: 18, fontWeight: '600', color: '#111827' },
  description: { fontSize: 14, color: '#4b5563' },
});
