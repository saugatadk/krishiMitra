import React from 'react';
import * as ReactNative from 'react-native';
import { View, StyleSheet, Platform } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import HomeScreen from './src/screens/HomeScreen';
import DiseaseDetectionScreen from './src/screens/DiseaseDetectionScreen';
import VoiceQueryScreen from './src/screens/VoiceQueryScreen';
import MarketPriceScreen from './src/screens/MarketPriceScreen';

import { LanguageProvider, useLanguage } from './src/context/LanguageContext';

// Polyfill InteractionManager for React Native 0.88 / Expo SDK 58
if (typeof ReactNative.InteractionManager === 'undefined' || !ReactNative.InteractionManager) {
  try {
    Object.defineProperty(ReactNative, 'InteractionManager', {
      configurable: true,
      enumerable: true,
      writable: true,
      value: {
        runAfterInteractions: (task) => {
          if (typeof task === 'function') {
            const id = setTimeout(task, 0);
            return { cancel: () => clearTimeout(id) };
          }
          return { cancel: () => {} };
        },
        createInteractionHandle: () => 1,
        clearInteractionHandle: () => {},
        setDeadline: () => {},
      },
    });
  } catch (e) {
    // Already defined or non-configurable
  }
}

const Stack = createStackNavigator();

function AppNavigator() {
  const { language } = useLanguage();
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerStyle: {
            backgroundColor: '#1b5e20',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        <Stack.Screen
          name="Home"
          component={HomeScreen}
          options={{ title: language === 'en' ? 'KrishiMitra' : 'कृषिमित्र' }}
        />
        <Stack.Screen
          name="DiseaseDetection"
          component={DiseaseDetectionScreen}
          options={{ title: language === 'en' ? 'Disease Detection' : 'रोग पहिचान' }}
        />
        <Stack.Screen
          name="VoiceQuery"
          component={VoiceQueryScreen}
          options={{ title: language === 'en' ? 'Voice Advisor' : 'कृषि सल्लाहकार' }}
        />
        <Stack.Screen
          name="MarketPrices"
          component={MarketPriceScreen}
          options={{ title: language === 'en' ? 'Market Rates' : 'बजार भाउ' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

export default function App() {
  return (
    <LanguageProvider>
      <View style={styles.outerContainer}>
        <View style={styles.mobileFrame}>
          <AppNavigator />
        </View>
      </View>
    </LanguageProvider>
  );
}

const styles = StyleSheet.create({
  outerContainer: {
    flex: 1,
    backgroundColor: Platform.OS === 'web' ? '#e2ece4' : '#f8fffe',
    ...(Platform.OS === 'web'
      ? {
          minHeight: '100vh',
          width: '100%',
          alignItems: 'center',
          justifyContent: 'flex-start',
          paddingVertical: 18,
          overflowY: 'auto',
          WebkitOverflowScrolling: 'touch',
        }
      : {}),
  },
  mobileFrame: {
    flex: 1,
    width: '100%',
    ...(Platform.OS === 'web'
      ? {
          maxWidth: 480,
          minHeight: 'calc(100vh - 36px)',
          backgroundColor: '#f8fffe',
          boxShadow: '0 12px 45px rgba(0,0,0,0.18)',
          borderRadius: 24,
          overflow: 'hidden',
          borderWidth: 1.5,
          borderColor: '#b2dfdb',
          display: 'flex',
          flexDirection: 'column',
        }
      : {}),
  },
});
