import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
  TouchableOpacity,
  ScrollView,
  Platform,
} from 'react-native';
import { getMarketPrices } from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import LanguageToggle from '../components/LanguageToggle';

const MARKET_KEYS = ['all', 'Birtamod', 'Taplejung', 'Ilam', 'Panchthar', 'Sankhuwasabha'];

export default function MarketPriceScreen() {
  const { t, language } = useLanguage();
  const [prices, setPrices] = useState([]);
  const [selectedMarket, setSelectedMarket] = useState('all');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [errorNotice, setErrorNotice] = useState(null);

  useEffect(() => {
    loadPrices();
  }, [selectedMarket]);

  const loadPrices = async () => {
    try {
      setErrorNotice(null);
      const filter = selectedMarket === 'all' ? null : selectedMarket;
      const data = await getMarketPrices(filter);
      setPrices(data);
    } catch (error) {
      console.warn('Error loading prices:', error.message);
      setErrorNotice(t('marketOffline'));
      // Graceful fallback data if completely disconnected
      if (prices.length === 0) {
        setPrices([
          { market: 'Birtamod', district: 'Jhapa', variety: 'Jhirse', price: 1065, price_per_man: 42600, trend: 'up', change: '+2.5%' },
          { market: 'Taplejung', district: 'Taplejung', variety: 'Ramsai', price: 1045, price_per_man: 41800, trend: 'stable', change: '0.0%' },
          { market: 'Ilam', district: 'Ilam', variety: 'Jhirse', price: 1055, price_per_man: 42200, trend: 'down', change: '-1.2%' },
        ]);
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadPrices();
  };

  const renderItem = ({ item }) => {
    const isUp = item.trend === 'up';
    const isDown = item.trend === 'down';
    const trendColor = isUp ? '#2e7d32' : isDown ? '#c62828' : '#757575';
    const trendIcon = isUp ? '📈' : isDown ? '📉' : '➖';

    return (
      <View style={styles.card}>
        <View style={styles.header}>
          <View style={styles.marketInfo}>
            <Text style={styles.marketName}>{item.market} {t('mandi')}</Text>
            <Text style={styles.marketLocation}>
              📍 {item.district || item.market} {t('districtLabel')} {item.variety ? `• ${item.variety}` : ''}
            </Text>
          </View>
          <View style={styles.trendContainer}>
            <Text style={styles.trendIcon}>{trendIcon}</Text>
            <Text style={[styles.change, { color: trendColor }]}>{item.change}</Text>
          </View>
        </View>

        <View style={styles.priceRow}>
          <View style={styles.priceContainer}>
            <Text style={styles.priceLabel}>{t('perKilogram')}</Text>
            <Text style={styles.price}>{t('rupees')} {Number(item.price).toLocaleString()}</Text>
          </View>

          <View style={styles.manPriceContainer}>
            <Text style={styles.priceLabel}>{t('perMonDetailed')}</Text>
            <Text style={styles.manPrice}>
              {t('rupees')} {item.price_per_man ? Number(item.price_per_man).toLocaleString() : (Number(item.price) * 40).toLocaleString()}
            </Text>
          </View>
        </View>

        <View style={styles.footer}>
          <Text style={styles.lastUpdated}>
            {item.recorded_date ? `${t('marketDateLabel')}: ${item.recorded_date}` : t('liveBadge')}
          </Text>
        </View>
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#2e7d32" />
        <Text style={styles.loadingText}>{t('marketRatesLoading')}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header Info */}
      <View style={styles.headerSection}>
        <Text style={styles.title}>📊 {t('marketHeaderTitle')}</Text>
        <Text style={styles.subtitle}>{t('marketHeaderSubtitle')}</Text>

        {/* Language Toggle */}
        <LanguageToggle style={{ marginBottom: 12 }} />

        {errorNotice && (
          <View style={styles.offlineBanner}>
            <Text style={styles.offlineText}>{errorNotice}</Text>
          </View>
        )}

        {/* Market Filter Chips */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.filterScroll}
        >
          {MARKET_KEYS.map((m) => {
            const isSelected = selectedMarket === m;
            const label = m === 'all' ? t('allMarkets') : m;
            return (
              <TouchableOpacity
                key={m}
                style={[styles.filterChip, isSelected && styles.filterChipSelected]}
                onPress={() => setSelectedMarket(m)}
                activeOpacity={0.8}
              >
                <Text style={[styles.filterChipText, isSelected && styles.filterChipTextSelected]}>
                  {label}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      </View>

      {/* Prices List */}
      <FlatList
        data={prices}
        style={{ flex: 1, ...(Platform.OS === 'web' ? { height: '100%', overflowY: 'auto' } : {}) }}
        renderItem={renderItem}
        keyExtractor={(item, index) => `${item.market}-${item.variety || index}`}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#2e7d32']} />
        }
        showsVerticalScrollIndicator={true}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>{t('marketEmpty')}</Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fffe',
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8fffe',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
    color: '#2e7d32',
    fontWeight: '500',
  },
  headerSection: {
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1b5e20',
    textAlign: 'center',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 13,
    color: '#666',
    textAlign: 'center',
    marginBottom: 10,
  },
  offlineBanner: {
    backgroundColor: '#fff3e0',
    padding: 8,
    borderRadius: 8,
    marginBottom: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#f57c00',
  },
  offlineText: {
    fontSize: 12,
    color: '#e65100',
  },
  filterScroll: {
    paddingVertical: 4,
  },
  filterChip: {
    backgroundColor: '#f1f8e9',
    paddingHorizontal: 14,
    paddingVertical: 7,
    borderRadius: 20,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#c5e1a5',
  },
  filterChipSelected: {
    backgroundColor: '#2e7d32',
    borderColor: '#2e7d32',
  },
  filterChipText: {
    fontSize: 13,
    color: '#2e7d32',
    fontWeight: '600',
  },
  filterChipTextSelected: {
    color: '#fff',
  },
  list: {
    padding: 16,
    paddingBottom: 120,
  },
  card: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 16,
    marginBottom: 14,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 6,
    elevation: 3,
    borderWidth: 1,
    borderColor: '#f0f0f0',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  marketInfo: {
    flex: 1,
  },
  marketName: {
    fontSize: 17,
    fontWeight: 'bold',
    color: '#1b5e20',
    marginBottom: 3,
  },
  marketLocation: {
    fontSize: 13,
    color: '#666',
  },
  trendContainer: {
    alignItems: 'flex-end',
  },
  trendIcon: {
    fontSize: 18,
    marginBottom: 2,
  },
  change: {
    fontSize: 13,
    fontWeight: 'bold',
  },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#f8fdf8',
    borderRadius: 12,
    padding: 12,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#e8f5e9',
  },
  priceContainer: {
    flex: 1,
    alignItems: 'center',
    borderRightWidth: 1,
    borderRightColor: '#e0e0e0',
  },
  manPriceContainer: {
    flex: 1,
    alignItems: 'center',
  },
  priceLabel: {
    fontSize: 11,
    color: '#777',
    marginBottom: 4,
  },
  price: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2e7d32',
  },
  manPrice: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1b5e20',
  },
  footer: {
    borderTopWidth: 1,
    borderTopColor: '#f5f5f5',
    paddingTop: 8,
  },
  lastUpdated: {
    fontSize: 11,
    color: '#999',
    textAlign: 'center',
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyText: {
    fontSize: 14,
    color: '#888',
  },
});
