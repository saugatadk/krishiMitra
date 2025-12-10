import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Dimensions } from 'react-native';

const { width } = Dimensions.get('window');

export default function HomeScreen({ navigation }) {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      {/* Header Section */}
      <View style={styles.headerSection}>
        <View style={styles.logoContainer}>
          <Text style={styles.logoIcon}>🌱</Text>
        </View>
        <Text style={styles.title}>Krishimitra</Text>
        <Text style={styles.subtitle}>Your Smart Cardamom Assistant</Text>
        <Text style={styles.description}>AI-powered farming solutions for better yields</Text>
      </View>

      {/* Features Grid */}
      <View style={styles.featuresGrid}>
        <TouchableOpacity 
          style={[styles.featureCard, styles.primaryCard]} 
          onPress={() => navigation.navigate('DiseaseDetection')}
          activeOpacity={0.8}
        >
          <View style={styles.cardIcon}>
            <Text style={styles.iconText}>📸</Text>
          </View>
          <Text style={styles.cardTitle}>Disease Detection</Text>
          <Text style={styles.cardSubtitle}>Identify plant diseases instantly</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.featureCard, styles.secondaryCard]} 
          onPress={() => navigation.navigate('VoiceQuery')}
          activeOpacity={0.8}
        >
          <View style={styles.cardIcon}>
            <Text style={styles.iconText}>🎤</Text>
          </View>
          <Text style={styles.cardTitle}>Ask Expert</Text>
          <Text style={styles.cardSubtitle}>Voice queries in Nepali</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.featureCard, styles.accentCard]} 
          onPress={() => navigation.navigate('MarketPrices')}
          activeOpacity={0.8}
        >
          <View style={styles.cardIcon}>
            <Text style={styles.iconText}>💰</Text>
          </View>
          <Text style={styles.cardTitle}>Market Prices</Text>
          <Text style={styles.cardSubtitle}>Live cardamom rates</Text>
        </TouchableOpacity>
      </View>

      {/* Footer Info */}
      <View style={styles.footerSection}>
        <Text style={styles.footerText}>Powered by AWS AI Services</Text>
        <Text style={styles.footerSubtext}>Helping Nepali farmers grow better</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fffe',
  },
  contentContainer: {
    flexGrow: 1,
    paddingHorizontal: 20,
    paddingTop: 40,
    paddingBottom: 30,
  },
  headerSection: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logoContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#e8f5e8',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  logoIcon: {
    fontSize: 36,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#1b5e20',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 18,
    color: '#388e3c',
    marginBottom: 8,
    textAlign: 'center',
    fontWeight: '500',
  },
  description: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginHorizontal: 30,
  },
  featuresGrid: {
    flex: 1,
    justifyContent: 'center',
  },
  featureCard: {
    backgroundColor: '#fff',
    borderRadius: 20,
    padding: 25,
    marginBottom: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 8,
    borderWidth: 1,
    borderColor: '#f0f0f0',
  },
  primaryCard: {
    backgroundColor: '#e8f5e8',
    borderColor: '#4caf50',
  },
  secondaryCard: {
    backgroundColor: '#fff3e0',
    borderColor: '#ff9800',
  },
  accentCard: {
    backgroundColor: '#e3f2fd',
    borderColor: '#2196f3',
  },
  cardIcon: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: 'rgba(255,255,255,0.9)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  iconText: {
    fontSize: 28,
  },
  cardTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1b5e20',
    marginBottom: 8,
    textAlign: 'center',
  },
  cardSubtitle: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    lineHeight: 20,
  },
  footerSection: {
    alignItems: 'center',
    marginTop: 30,
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  footerText: {
    fontSize: 14,
    color: '#388e3c',
    fontWeight: '500',
    marginBottom: 4,
  },
  footerSubtext: {
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
  },
});
