import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, RefreshControl, Platform } from 'react-native';
import { checkHealth, getMarketPrices } from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import LanguageToggle from '../components/LanguageToggle';

export default function HomeScreen({ navigation }) {
  const { t, language } = useLanguage();
  const [tickerPrice, setTickerPrice] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadHomeData();
  }, []);

  const loadHomeData = async () => {
    try {
      // 1. Silent Health check
      await checkHealth();

      // 2. Ticker price for Birtamod
      const prices = await getMarketPrices();
      if (prices && prices.length > 0) {
        setTickerPrice(prices[0]);
      }
    } catch (e) {
      console.warn('Home data load error:', e);
    } finally {
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadHomeData();
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.contentContainer}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#2e7d32']} />
      }
    >
      {/* Header Section */}
      <View style={styles.headerSection}>
        <View style={styles.logoContainer}>
          <Text style={styles.logoIcon}>🌱</Text>
        </View>
        <Text style={styles.title}>{t('appTitle')}</Text>
        <Text style={styles.subtitle}>{t('homeSubtitle')}</Text>

        {/* English & Nepali Language Toggle */}
        <LanguageToggle style={styles.languageToggleRow} />
      </View>

      {/* Live Market Price Ticker Card */}
      {tickerPrice && (
        <TouchableOpacity
          style={styles.tickerCard}
          onPress={() => navigation.navigate('MarketPrices')}
          activeOpacity={0.8}
        >
          <View style={styles.tickerHeader}>
            <Text style={styles.tickerBadge}>{t('liveBadge')}</Text>
            <Text style={styles.tickerMarket}>📍 {tickerPrice.market} {t('mandi')}</Text>
          </View>
          <View style={styles.tickerBody}>
            <Text style={styles.tickerPrice}>
              {t('rupees')} {Number(tickerPrice.price).toLocaleString()} / {t('perKg')}
            </Text>
            <Text style={styles.tickerTrend}>
              {tickerPrice.trend === 'up' ? '📈' : tickerPrice.trend === 'down' ? '📉' : '➖'}{' '}
              {tickerPrice.change}
            </Text>
          </View>
          <Text style={styles.tickerSubtext}>
            {t('perMon')} {tickerPrice.price_per_man
              ? Number(tickerPrice.price_per_man).toLocaleString()
              : (Number(tickerPrice.price) * 40).toLocaleString()}
          </Text>
        </TouchableOpacity>
      )}

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
          <Text style={styles.cardTitle}>{t('diseaseTitle')}</Text>
          <Text style={styles.cardSubtitle}>{t('diseaseDesc')}</Text>
          <View style={styles.cardBadge}>
            <Text style={styles.cardBadgeText}>{t('diseaseBadge')}</Text>
          </View>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.featureCard, styles.secondaryCard]}
          onPress={() => navigation.navigate('VoiceQuery')}
          activeOpacity={0.8}
        >
          <View style={styles.cardIcon}>
            <Text style={styles.iconText}>🎤</Text>
          </View>
          <Text style={styles.cardTitle}>{t('voiceTitle')}</Text>
          <Text style={styles.cardSubtitle}>{t('voiceDesc')}</Text>
          <View style={styles.cardBadge}>
            <Text style={styles.cardBadgeText}>{t('voiceBadge')}</Text>
          </View>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.featureCard, styles.accentCard]}
          onPress={() => navigation.navigate('MarketPrices')}
          activeOpacity={0.8}
        >
          <View style={styles.cardIcon}>
            <Text style={styles.iconText}>💰</Text>
          </View>
          <Text style={styles.cardTitle}>{t('marketTitle')}</Text>
          <Text style={styles.cardSubtitle}>{t('marketDesc')}</Text>
          <View style={styles.cardBadge}>
            <Text style={styles.cardBadgeText}>{t('marketBadge')}</Text>
          </View>
        </TouchableOpacity>
      </View>

      {/* Footer Info */}
      <View style={styles.footerSection}>
        <Text style={styles.footerText}>
          {language === 'en'
            ? 'Dedicated to empowering large cardamom farmers with cutting-edge AI'
            : 'नेपाली किसानहरूको समृद्धिका लागि समर्पित'}
        </Text>
        <Text style={styles.footerSubtext}>KrishiMitra Smart Farming Suite • Version 1.0</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fffe',
    ...(Platform.OS === 'web'
      ? {
          height: '100%',
          overflowY: 'auto',
          WebkitOverflowScrolling: 'touch',
        }
      : {}),
  },
  contentContainer: {
    flexGrow: 1,
    paddingHorizontal: 20,
    paddingTop: 30,
    paddingBottom: 100,
  },
  headerSection: {
    alignItems: 'center',
    marginBottom: 20,
  },
  logoContainer: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: '#e8f5e8',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 4,
  },
  logoIcon: {
    fontSize: 34,
  },
  title: {
    fontSize: 26,
    fontWeight: 'bold',
    color: '#1b5e20',
    marginBottom: 4,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 15,
    color: '#388e3c',
    marginBottom: 6,
    textAlign: 'center',
    fontWeight: '500',
  },
  languageToggleRow: {
    marginTop: 6,
    marginBottom: 4,
  },
  cardBadge: {
    marginTop: 8,
    backgroundColor: 'rgba(255,255,255,0.85)',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 8,
    alignSelf: 'center',
  },
  cardBadgeText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#2e7d32',
  },
  tickerCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 6,
    elevation: 3,
    borderWidth: 1,
    borderColor: '#e8f5e9',
  },
  tickerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  tickerBadge: {
    backgroundColor: '#e8f5e9',
    color: '#2e7d32',
    fontSize: 11,
    fontWeight: 'bold',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  tickerMarket: {
    fontSize: 13,
    fontWeight: '600',
    color: '#555',
  },
  tickerBody: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  tickerPrice: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#1b5e20',
  },
  tickerTrend: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#2e7d32',
  },
  tickerSubtext: {
    fontSize: 12,
    color: '#777',
    marginTop: 4,
  },
  featuresGrid: {
    flex: 1,
  },
  featureCard: {
    backgroundColor: '#fff',
    borderRadius: 18,
    padding: 20,
    marginBottom: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 4,
    borderWidth: 1.5,
  },
  primaryCard: {
    backgroundColor: '#f1f8e9',
    borderColor: '#81c784',
  },
  secondaryCard: {
    backgroundColor: '#fff8e1',
    borderColor: '#ffb74d',
  },
  accentCard: {
    backgroundColor: '#e3f2fd',
    borderColor: '#64b5f6',
  },
  cardIcon: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: 'rgba(255,255,255,0.95)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 2,
  },
  iconText: {
    fontSize: 26,
  },
  cardTitle: {
    fontSize: 17,
    fontWeight: 'bold',
    color: '#1b5e20',
    marginBottom: 4,
    textAlign: 'center',
  },
  cardSubtitle: {
    fontSize: 13,
    color: '#666',
    textAlign: 'center',
    lineHeight: 18,
  },
  footerSection: {
    alignItems: 'center',
    marginTop: 20,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  footerText: {
    fontSize: 13,
    color: '#388e3c',
    fontWeight: '500',
    marginBottom: 4,
  },
  footerSubtext: {
    fontSize: 11,
    color: '#999',
    textAlign: 'center',
  },
});
