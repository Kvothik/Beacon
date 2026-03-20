import { useEffect, useState } from 'react';
import { ActivityIndicator, View, Text } from 'react-native';
import { NavigationContainer, DefaultTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import { authService } from '../services/authService';
import { useAuthStore } from '../store/authStore';
import HomeScreen from '../screens/HomeScreen';
import LoginScreen from '../screens/LoginScreen';
import PacketBuilderScreen from '../screens/PacketBuilderScreen';
import PdfPreviewScreen from '../screens/PdfPreviewScreen';
import RegisterScreen from '../screens/RegisterScreen';
import ReviewScreen from '../screens/ReviewScreen';
import ScannerScreen from '../screens/ScannerScreen';
import SectionDetailScreen from '../screens/SectionDetailScreen';
import type { PacketSectionKey } from '../types/packet';

export type AppStackParamList = {
  Login: undefined;
  Register: undefined;
  Home: undefined;
  PacketBuilder: undefined;
  SectionDetail: { sectionKey: PacketSectionKey };
  Scanner: { sectionKey: PacketSectionKey };
  Review: undefined;
  PdfPreview: undefined;
};

const Stack = createNativeStackNavigator<AppStackParamList>();

const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    background: '#f5f7fb',
  },
};

function AuthBootstrap() {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <ActivityIndicator size="large" color="#111827" />
      <Text>Loading Splash Screen (Autonomous Debug)</Text>
    </View>
  );
}

export default function BeaconNavigator() {
  const { isHydrated, isAuthenticated, session } = useAuthStore();
  const [hydrationTimedOut, setHydrationTimedOut] = useState(false);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    async function doHydrate() {
      console.log('[AppNavigator] hydrateSession start');
      try {
        await authService.hydrateSession();
        console.log('[AppNavigator] hydrateSession success');
      } catch (e) {
        console.log('[AppNavigator] hydrateSession failure', e);
      } finally {
        console.log('[AppNavigator] hydrateSession finally');
        clearTimeout(timeoutId);
      }
    }

    doHydrate();

    timeoutId = setTimeout(() => {
      console.log('[AppNavigator] Hydration timeout');
      setHydrationTimedOut(true);
    }, 10000); // 10 seconds timeout
  }, []);

  console.log(`[AppNavigator] isHydrated: ${isHydrated} hydrationTimedOut: ${hydrationTimedOut} isAuthenticated: ${isAuthenticated} session: ${session}`);

  if (!isHydrated && !hydrationTimedOut) {
    console.log('[AppNavigator] Waiting for hydration');
    return <AuthBootstrap />;
  }

  return (
    <NavigationContainer theme={theme}>
      <Stack.Navigator>
        {isAuthenticated ? (
          <>
            <Stack.Screen name="Home" component={HomeScreen} options={{ title: 'Beacon' }} />
            <Stack.Screen name="PacketBuilder" component={PacketBuilderScreen} options={{ title: 'Packet Builder' }} />
            <Stack.Screen name="SectionDetail" component={SectionDetailScreen} options={{ title: 'Section Detail' }} />
            <Stack.Screen name="Scanner" component={ScannerScreen} options={{ title: 'Scanner' }} />
            <Stack.Screen name="Review" component={ReviewScreen} options={{ title: 'Review' }} />
            <Stack.Screen name="PdfPreview" component={PdfPreviewScreen} options={{ title: 'PDF Export' }} />
          </>
        ) : (
          <>
            <Stack.Screen name="Login" component={LoginScreen} options={{ title: 'Sign In' }} />
            <Stack.Screen name="Register" component={RegisterScreen} options={{ title: 'Create Account' }} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
