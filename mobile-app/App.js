import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import HomeScreen from './src/screens/HomeScreen';
import DiseaseDetectionScreen from './src/screens/DiseaseDetectionScreen';
import VoiceQueryScreen from './src/screens/VoiceQueryScreen';
import MarketPriceScreen from './src/screens/MarketPriceScreen';

const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen name="Home" component={HomeScreen} options={{ title: 'Krishimitra' }} />
        <Stack.Screen name="DiseaseDetection" component={DiseaseDetectionScreen} options={{ title: 'Disease Detection' }} />
        <Stack.Screen name="VoiceQuery" component={VoiceQueryScreen} options={{ title: 'Ask Expert' }} />
        <Stack.Screen name="MarketPrices" component={MarketPriceScreen} options={{ title: 'Market Prices' }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
