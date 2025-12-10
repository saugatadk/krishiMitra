import React, { useState, useEffect } from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet, ActivityIndicator, Alert, ScrollView, Platform } from 'react-native';
import * as ImagePicker from 'expo-image-picker';

export default function DiseaseDetectionScreen() {
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const pickImage = async () => {
    try {
      // Request permission for all platforms
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Required', 'Please grant permission to access your photo library in device settings.');
        return;
      }

      let result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: 'Images',
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
        base64: false,
      });

      if (!result.canceled && result.assets && result.assets[0]) {
        setImage(result.assets[0].uri);
        setResult(null);
      }
    } catch (error) {
      console.error('Image picker error:', error);
      Alert.alert('Error', 'Failed to access gallery. Please check permissions and try again.');
    }
  };

  const takePhoto = async () => {
    try {
      const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
      if (permissionResult.granted === false) {
        Alert.alert("Camera Permission", "Please grant camera permission in device settings.");
        return;
      }
      
      let result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets[0]) {
        setImage(result.assets[0].uri);
        setResult(null);
      }
    } catch (error) {
      console.error('Camera error:', error);
      Alert.alert('Error', 'Failed to access camera. Please check permissions and try again.');
    }
  };

  const handleAnalyze = async () => {
    if (!image) return;

    setLoading(true);
    try {
      // Simulate disease detection with mock data
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate API delay
      
      const mockResult = {
        diagnosis: [
          { Name: 'Cardamom Leaf Blight', Confidence: 89.5 },
          { Name: 'Healthy', Confidence: 10.5 }
        ],
        treatment: {
          disease: 'Cardamom Leaf Blight',
          severity: 'Moderate',
          treatment_plan: [
            'Remove affected leaves immediately',
            'Apply copper-based fungicide (Bordeaux mixture)',
            'Improve air circulation around plants',
            'Reduce watering frequency',
            'Apply organic neem oil spray weekly'
          ],
          prevention: [
            'Avoid overhead watering',
            'Maintain proper plant spacing',
            'Remove plant debris regularly',
            'Apply preventive fungicide during monsoon'
          ],
          expected_recovery: '2-3 weeks with proper treatment'
        },
        alert_sent: true
      };
      
      setResult(mockResult);
      if (mockResult.alert_sent) {
        Alert.alert("⚠️ Disease Detected", "Cardamom Leaf Blight detected! SMS alert sent to registered number.");
      }
    } catch (error) {
      Alert.alert("Error", "Failed to analyze image. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      <Text style={styles.title}>Disease Detection</Text>
      <Text style={styles.subtitle}>Upload or capture a photo of your cardamom plant</Text>

      <View style={styles.buttonContainer}>
        <TouchableOpacity style={styles.actionButton} onPress={pickImage}>
          <Text style={styles.buttonIcon}>📱</Text>
          <Text style={styles.buttonText}>Gallery</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.actionButton} onPress={takePhoto}>
          <Text style={styles.buttonIcon}>📸</Text>
          <Text style={styles.buttonText}>Camera</Text>
        </TouchableOpacity>
      </View>

      {image && (
        <View style={styles.imageContainer}>
          <Image source={{ uri: image }} style={styles.image} />
        </View>
      )}

      {image && !loading && !result && (
        <TouchableOpacity style={styles.analyzeButton} onPress={handleAnalyze}>
          <Text style={styles.analyzeButtonText}>🔍 Analyze Plant</Text>
        </TouchableOpacity>
      )}

      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#2e7d32" />
          <Text style={styles.loadingText}>Analyzing your plant...</Text>
        </View>
      )}

      {result && (
        <View style={styles.resultContainer}>
          <View style={styles.diagnosisSection}>
            <Text style={styles.sectionTitle}>🔬 Diagnosis</Text>
            {result.diagnosis.map((item, index) => (
              <View key={index} style={styles.diagnosisItem}>
                <Text style={styles.diseaseName}>{item.Name}</Text>
                <Text style={styles.confidence}>{item.Confidence.toFixed(1)}%</Text>
              </View>
            ))}
          </View>

          {result.treatment && (
            <View style={styles.treatmentSection}>
              <Text style={styles.sectionTitle}>💊 Treatment Plan</Text>
              <View style={styles.severityBadge}>
                <Text style={styles.severityText}>Severity: {result.treatment.severity}</Text>
              </View>
              
              <View style={styles.treatmentSteps}>
                <Text style={styles.stepTitle}>Immediate Actions:</Text>
                {result.treatment.treatment_plan.map((step, index) => (
                  <Text key={index} style={styles.stepText}>• {step}</Text>
                ))}
              </View>

              <View style={styles.preventionSteps}>
                <Text style={styles.stepTitle}>Prevention Tips:</Text>
                {result.treatment.prevention.map((tip, index) => (
                  <Text key={index} style={styles.stepText}>• {tip}</Text>
                ))}
              </View>

              <View style={styles.recoveryInfo}>
                <Text style={styles.recoveryTitle}>Expected Recovery:</Text>
                <Text style={styles.recoveryText}>{result.treatment.expected_recovery}</Text>
              </View>
            </View>
          )}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fffe',
  },
  contentContainer: {
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1b5e20',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 30,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 30,
  },
  actionButton: {
    backgroundColor: '#fff',
    paddingVertical: 20,
    paddingHorizontal: 30,
    borderRadius: 15,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
    borderWidth: 2,
    borderColor: '#4caf50',
  },
  buttonIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  buttonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2e7d32',
  },
  imageContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  image: {
    width: 280,
    height: 280,
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 10,
    elevation: 8,
  },
  analyzeButton: {
    backgroundColor: '#4caf50',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 25,
    alignItems: 'center',
    marginVertical: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 6,
  },
  analyzeButtonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  loadingContainer: {
    alignItems: 'center',
    marginVertical: 30,
  },
  loadingText: {
    fontSize: 16,
    color: '#2e7d32',
    marginTop: 10,
  },
  resultContainer: {
    marginTop: 20,
  },
  diagnosisSection: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 15,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1b5e20',
    marginBottom: 15,
  },
  diagnosisItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  diseaseName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  confidence: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#f44336',
    backgroundColor: '#ffebee',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  treatmentSection: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  severityBadge: {
    backgroundColor: '#ff5722',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    alignSelf: 'flex-start',
    marginBottom: 20,
  },
  severityText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 14,
  },
  treatmentSteps: {
    marginBottom: 20,
  },
  preventionSteps: {
    marginBottom: 20,
  },
  stepTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2e7d32',
    marginBottom: 10,
  },
  stepText: {
    fontSize: 14,
    color: '#555',
    marginBottom: 8,
    lineHeight: 20,
    paddingLeft: 10,
  },
  recoveryInfo: {
    backgroundColor: '#e8f5e8',
    padding: 15,
    borderRadius: 10,
    marginTop: 10,
  },
  recoveryTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2e7d32',
    marginBottom: 5,
  },
  recoveryText: {
    fontSize: 14,
    color: '#388e3c',
    fontWeight: '500',
  },
});
