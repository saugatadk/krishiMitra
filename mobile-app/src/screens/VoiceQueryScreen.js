import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, ScrollView } from 'react-native';

export default function VoiceQueryScreen() {
  const [recording, setRecording] = useState();
  const [loading, setLoading] = useState(false);
  const [queryText, setQueryText] = useState('');
  const [responseText, setResponseText] = useState('');

  async function startRecording() {
    setRecording(true);
    // Simulate recording start
    setTimeout(() => {
      // Auto-stop after 5 seconds for demo
      if (recording) {
        stopRecording();
      }
    }, 5000);
  }

  async function stopRecording() {
    setRecording(false);
    handleSendQuery();
  }

  const handleSendQuery = async () => {
    setLoading(true);
    setQueryText('');
    setResponseText('');
    
    try {
      // Simulate processing delay
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Mock Nepali query and response
      const mockData = {
        query_text: "मेरो अलैंची बगानमा पातहरू पहेंलो भएका छन्। के गर्ने?",
        response: "तपाईंको अलैंचीका पातहरू पहेंलो हुनुको मुख्य कारणहरू:\n\n🌱 सम्भावित कारणहरू:\n• नाइट्रोजनको कमी\n• पानीको अधिकता वा कमी\n• माटोमा आइरनको कमी\n• जराको सड्ने रोग\n\n💊 समाधानहरू:\n• प्राकृतिक मल (कम्पोस्ट) प्रयोग गर्नुहोस्\n• पानी दिने मात्रा नियन्त्रण गर्नुहोस्\n• माटोको ड्रेनेज सुधार गर्नुहोस्\n• आइरन सल्फेट घोल छर्कनुहोस्\n\n⚠️ सुझावः यदि समस्या बढ्दै गयो भने स्थानीय कृषि विज्ञलाई सम्पर्क गर्नुहोस्।"
      };
      
      setQueryText(mockData.query_text);
      setResponseText(mockData.response);
    } catch (error) {
      setResponseText("Error processing your query. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.instructions}>
        Tap the microphone to ask a question in Nepali about your cardamom farm.
      </Text>

      <View style={styles.micContainer}>
        <TouchableOpacity 
          style={[styles.micButton, recording && styles.micButtonRecording]}
          onPress={recording ? stopRecording : startRecording}
        >
          <Text style={styles.micIcon}>{recording ? '🔴' : '🎤'}</Text>
          <Text style={styles.micText}>
            {recording ? 'Recording... Tap to stop' : 'Tap to ask in Nepali'}
          </Text>
        </TouchableOpacity>
      </View>

      {loading && <ActivityIndicator size="large" color="#2e7d32" style={{marginTop: 20}} />}

      {queryText ? (
        <View style={styles.chatContainer}>
          <Text style={styles.label}>You asked:</Text>
          <Text style={styles.queryText}>{queryText}</Text>
          
          <View style={styles.divider} />
          
          <Text style={styles.label}>Expert Answer:</Text>
          <Text style={styles.responseText}>{responseText}</Text>
        </View>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    padding: 20,
    backgroundColor: '#f8fffe',
  },
  instructions: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 30,
    color: '#666',
    lineHeight: 24,
  },
  micContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  micButton: {
    backgroundColor: '#4caf50',
    paddingVertical: 30,
    paddingHorizontal: 40,
    borderRadius: 50,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 10,
  },
  micButtonRecording: {
    backgroundColor: '#f44336',
  },
  micIcon: {
    fontSize: 40,
    marginBottom: 10,
  },
  micText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
    textAlign: 'center',
  },
  chatContainer: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  label: {
    fontWeight: 'bold',
    color: '#2e7d32',
    marginBottom: 8,
    fontSize: 16,
  },
  queryText: {
    fontSize: 16,
    fontStyle: 'italic',
    marginBottom: 15,
    color: '#555',
    backgroundColor: '#f0f9f0',
    padding: 15,
    borderRadius: 10,
    lineHeight: 24,
  },
  divider: {
    height: 1,
    backgroundColor: '#e0e0e0',
    marginBottom: 15,
  },
  responseText: {
    fontSize: 16,
    lineHeight: 24,
    color: '#333',
  },
});
