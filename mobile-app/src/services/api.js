import axios from 'axios';
import { Platform } from 'react-native';
import Constants from 'expo-constants';

/**
 * Smart Base URL resolution:
 * - Physical devices running Expo Go extract host IP from Metro connection
 * - Web uses 127.0.0.1:8000
 * - Fallback to workstation LAN IP (192.168.100.38)
 */
const DEFAULT_LAN_IP = '192.168.100.38';
let CUSTOM_BACKEND_IP = null;

export const setCustomBackendIp = (ip) => {
  CUSTOM_BACKEND_IP = ip;
};

export const getApiBaseUrl = () => {
  if (CUSTOM_BACKEND_IP) {
    return `http://${CUSTOM_BACKEND_IP}:8000/api`;
  }
  if (Platform.OS === 'web') {
    return 'http://127.0.0.1:8000/api';
  }

  // Auto-detect host IP when running in Expo Go on mobile
  const hostUri = Constants.expoConfig?.hostUri 
    || Constants.manifest2?.extra?.expoClient?.hostUri 
    || Constants.manifest?.debuggerHost;

  if (hostUri) {
    const hostIp = hostUri.split(':')[0];
    if (hostIp && hostIp !== 'localhost' && hostIp !== '127.0.0.1') {
      return `http://${hostIp}:8000/api`;
    }
  }

  if (DEFAULT_LAN_IP) {
    return `http://${DEFAULT_LAN_IP}:8000/api`;
  }

  if (Platform.OS === 'android') {
    return 'http://10.0.2.2:8000/api';
  }
  return 'http://127.0.0.1:8000/api';
};

const createApiClient = () => {
  return axios.create({
    baseURL: getApiBaseUrl(),
    timeout: 30000,
  });
};

/**
 * Check backend health & database connection
 */
export const checkHealth = async () => {
  try {
    const client = createApiClient();
    const response = await client.get('/health/');
    return response.data;
  } catch (error) {
    console.warn('Backend health check failed:', error.message);
    return { status: 'offline', error: error.message };
  }
};

/**
 * Upload cardamom leaf image for AI diagnosis and treatment plan
 */
export const detectDisease = async (imageUri) => {
  if (Platform.OS === 'web') {
    try {
      const formData = new FormData();
      const res = await fetch(imageUri);
      const blob = await res.blob();
      const safeFilename = imageUri.includes('.png') ? 'crop_leaf.png' : 'crop_leaf.jpg';
      formData.append('image', blob, safeFilename);

      const response = await fetch(`${getApiBaseUrl()}/disease-detect/`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        // If formData failed on web, try base64 fallback
        if (imageUri.startsWith('data:')) {
          const jsonRes = await fetch(`${getApiBaseUrl()}/disease-detect/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageUri }),
          });
          if (jsonRes.ok) return await jsonRes.json();
        }
        const errText = await response.text();
        throw new Error(`Server returned ${response.status}: ${errText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error detecting disease on web:', error);
      throw error;
    }
  }

  // Mobile native (Android/iOS)
  const formData = new FormData();
  const filename = imageUri.split('/').pop() || 'crop_leaf.jpg';
  const match = /\.(\w+)$/.exec(filename);
  const type = match ? `image/${match[1]}` : 'image/jpeg';

  formData.append('image', {
    uri: Platform.OS === 'android' ? imageUri : imageUri.replace('file://', ''),
    name: filename,
    type: type,
  });

  try {
    const client = createApiClient();
    const response = await client.post('/disease-detect/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error detecting disease:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Synchronize batch of offline inspections with backend database
 */
export const syncOfflineInspections = async (inspections) => {
  try {
    const client = createApiClient();
    const response = await client.post('/disease-detect/sync/', { inspections });
    return response.data;
  } catch (error) {
    console.error('Error syncing offline inspections:', error.message);
    throw error;
  }
};

/**
 * Upload recorded Nepali voice query and receive advice + spoken audio
 */
export const sendVoiceQuery = async (audioUri) => {
  if (Platform.OS === 'web') {
    try {
      const formData = new FormData();
      const res = await fetch(audioUri);
      const blob = await res.blob();
      formData.append('audio', blob, 'voice_query.wav');

      const response = await fetch(`${getApiBaseUrl()}/voice-query/`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Server returned ${response.status}: ${errText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error sending voice query on web:', error);
      throw error;
    }
  }

  const formData = new FormData();
  const filename = audioUri.split('/').pop() || 'voice_query.m4a';
  const match = /\.(\w+)$/.exec(filename);
  const ext = match ? match[1] : 'm4a';

  formData.append('audio', {
    uri: Platform.OS === 'android' ? audioUri : audioUri.replace('file://', ''),
    name: filename,
    type: `audio/${ext}`,
  });

  try {
    const client = createApiClient();
    const response = await client.post('/voice-query/', formData);
    return response.data;
  } catch (error) {
    console.error('Error sending voice query:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Fetch live cardamom market rates across Nepal
 */
export const getMarketPrices = async (marketFilter = null) => {
  try {
    const client = createApiClient();
    const url = marketFilter ? `/market-prices/?market=${encodeURIComponent(marketFilter)}` : '/market-prices/';
    const response = await client.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching market prices:', error.message);
    throw error;
  }
};
