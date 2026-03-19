import AppNavigator from './src/navigation/AppNavigator';

import React, { useEffect } from 'react';
import AppNavigator from './src/navigation/AppNavigator';

export default function App() {
  useEffect(() => {
    console.log('[App.tsx] App mounted');
  }, []);

  return <AppNavigator />;
}

