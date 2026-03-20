import React, { useEffect } from 'react';
import BeaconNavigator from './src/navigation/AppNavigator';

export default function App() {
  useEffect(() => {
    console.log('[App.tsx] App mounted');
  }, []);

  return <BeaconNavigator />;
}

