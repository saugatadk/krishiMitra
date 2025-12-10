import axios from 'axios';

// Use localhost for web testing, update for device testing
const API_BASE_URL = 'http://127.0.0.1:8000/api'; 

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

export const detectDisease = async (imageUri) => {
  const formData = new FormData();
  formData.append('image', {
    uri: imageUri,
    type: 'image/jpeg',
    name: 'upload.jpg',
  });

  try {
    const response = await api.post('/disease-detect/', formData);
    return response.data;
  } catch (error) {
    console.error('Error detecting disease:', error);
    throw error;
  }
};

export const sendVoiceQuery = async (audioUri) => {
  const formData = new FormData();
  formData.append('audio', {
    uri: audioUri,
    type: 'audio/mp3', // Adjust based on actual recording format
    name: 'query.mp3',
  });

  try {
    const response = await api.post('/voice-query/', formData);
    return response.data;
  } catch (error) {
    console.error('Error sending voice query:', error);
    throw error;
  }
};

export const getMarketPrices = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/market-prices/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching prices:', error);
    throw error;
  }
};
