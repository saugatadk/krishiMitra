import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator, RefreshControl, TouchableOpacity } from 'react-native';

export default function MarketPriceScreen() {
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadPrices();
  }, []);

  const loadPrices = async () => {
    try {
      // Simulate loading delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock market data - prices per kg
      const mockPrices = [
        { market: "Birtamod", price: 1050, trend: "up", change: "+2.5%" },
        { market: "Taplejung", price: 1038, trend: "stable", change: "0%" },
        { market: "Ilam", price: 1055, trend: "down", change: "-1.2%" },
        { market: "Jhapa", price: 1045, trend: "up", change: "+1.8%" },
        { market: "Panchthar", price: 1023, trend: "down", change: "-0.8%" },
        { market: "Dhankuta", price: 1033, trend: "stable", change: "+0.2%" },
      ];
      
      setPrices(mockPrices);
    } catch (error) {
      console.error('Error loading prices:', error);
      // Set fallback data even on error - prices per kg
      setPrices([
        { market: "Birtamod", price: 1050, trend: "up", change: "+2.5%" },
        { market: "Taplejung", price: 1038, trend: "stable", change: "0%" },
        { market: "Ilam", price: 1055, trend: "down", change: "-1.2%" },
      ]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadPrices();
  };

  const renderItem = ({ item }) => (
    <TouchableOpacity style={styles.card} activeOpacity={0.7}>
      <View style={styles.header}>
        <View style={styles.marketInfo}>
          <Text style={styles.marketName}>{item.market}</Text>
          <Text style={styles.marketLocation}>📍 {item.market} Market</Text>
        </View>
        <View style={styles.trendContainer}>
          <Text style={[
            styles.trendIcon, 
            { color: item.trend === 'up' ? '#4caf50' : item.trend === 'down' ? '#f44336' : '#9e9e9e' }
          ]}>
            {item.trend === 'up' ? '📈' : item.trend === 'down' ? '📉' : '➖'}
          </Text>
          <Text style={[
            styles.change,
            { color: item.trend === 'up' ? '#4caf50' : item.trend === 'down' ? '#f44336' : '#9e9e9e' }
          ]}>
            {item.change}
          </Text>
        </View>
      </View>
      <View style={styles.priceContainer}>
        <Text style={styles.price}>₹ {item.price.toLocaleString()}</Text>
        <Text style={styles.unit}>per kg</Text>
      </View>
      <View style={styles.footer}>
        <Text style={styles.lastUpdated}>Last updated: Just now</Text>
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#2e7d32" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.headerSection}>
        <Text style={styles.title}>📊 Market Prices</Text>
        <Text style={styles.subtitle}>Live Cardamom Rates Across Nepal</Text>
      </View>
      
      <FlatList
        data={prices}
        renderItem={renderItem}
        keyExtractor={(item) => item.market}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
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
  },
  headerSection: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
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
  },
  list: {
    padding: 15,
    paddingBottom: 30,
  },
  card: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
    borderWidth: 1,
    borderColor: '#f0f0f0',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 15,
  },
  marketInfo: {
    flex: 1,
  },
  marketName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1b5e20',
    marginBottom: 4,
  },
  marketLocation: {
    fontSize: 14,
    color: '#666',
  },
  trendContainer: {
    alignItems: 'center',
  },
  trendIcon: {
    fontSize: 20,
    marginBottom: 4,
  },
  change: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  priceContainer: {
    alignItems: 'center',
    marginBottom: 15,
    backgroundColor: '#f8f9fa',
    padding: 15,
    borderRadius: 10,
  },
  price: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2e7d32',
    marginBottom: 4,
  },
  unit: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  footer: {
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    paddingTop: 10,
  },
  lastUpdated: {
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
    fontStyle: 'italic',
  },
});
