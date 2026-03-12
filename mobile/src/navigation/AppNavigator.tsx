import { NavigationContainer, DefaultTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import HomeScreen from '../screens/HomeScreen';
import LoginScreen from '../screens/LoginScreen';
import PacketBuilderScreen from '../screens/PacketBuilderScreen';
import PdfPreviewScreen from '../screens/PdfPreviewScreen';
import RegisterScreen from '../screens/RegisterScreen';
import ReviewScreen from '../screens/ReviewScreen';
import ScannerScreen from '../screens/ScannerScreen';
import SectionDetailScreen from '../screens/SectionDetailScreen';

export type AppStackParamList = {
  Login: undefined;
  Register: undefined;
  Home: undefined;
  PacketBuilder: undefined;
  SectionDetail: undefined;
  Scanner: undefined;
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

export default function AppNavigator() {
  return (
    <NavigationContainer theme={theme}>
      <Stack.Navigator initialRouteName="Login">
        <Stack.Screen name="Login" component={LoginScreen} options={{ title: 'Sign In' }} />
        <Stack.Screen name="Register" component={RegisterScreen} options={{ title: 'Create Account' }} />
        <Stack.Screen name="Home" component={HomeScreen} options={{ title: 'Beacon' }} />
        <Stack.Screen name="PacketBuilder" component={PacketBuilderScreen} options={{ title: 'Packet Builder' }} />
        <Stack.Screen name="SectionDetail" component={SectionDetailScreen} options={{ title: 'Section Detail' }} />
        <Stack.Screen name="Scanner" component={ScannerScreen} options={{ title: 'Scanner' }} />
        <Stack.Screen name="Review" component={ReviewScreen} options={{ title: 'Review' }} />
        <Stack.Screen name="PdfPreview" component={PdfPreviewScreen} options={{ title: 'PDF Preview' }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
