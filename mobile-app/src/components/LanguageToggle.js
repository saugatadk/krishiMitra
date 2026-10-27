import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useLanguage } from '../context/LanguageContext';

export default function LanguageToggle({ style }) {
  const { language, setLanguage } = useLanguage();

  return (
    <View style={[styles.container, style]}>
      <TouchableOpacity
        style={[styles.pillOption, language === 'ne' && styles.pillActive]}
        onPress={() => setLanguage('ne')}
        activeOpacity={0.8}
      >
        <Text style={[styles.pillText, language === 'ne' && styles.pillTextActive]}>
          🇳🇵 नेपाली
        </Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={[styles.pillOption, language === 'en' && styles.pillActive]}
        onPress={() => setLanguage('en')}
        activeOpacity={0.8}
      >
        <Text style={[styles.pillText, language === 'en' && styles.pillTextActive]}>
          🇬🇧 English
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: '#e8f5e9',
    borderRadius: 24,
    padding: 3,
    borderWidth: 1,
    borderColor: '#c8e6c9',
    alignSelf: 'center',
    marginVertical: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 3,
    elevation: 2,
  },
  pillOption: {
    paddingVertical: 6,
    paddingHorizontal: 14,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  pillActive: {
    backgroundColor: '#2e7d32',
    shadowColor: '#1b5e20',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3,
    elevation: 3,
  },
  pillText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#2e7d32',
  },
  pillTextActive: {
    color: '#ffffff',
    fontWeight: 'bold',
  },
});
