import React, { createContext, useContext, useState } from 'react';

const LanguageContext = createContext();

export const TRANSLATIONS = {
  ne: {
    appTitle: 'कृषिमित्र',
    homeSubtitle: 'नेपाली अलैंची किसानको स्मार्ट साथी',
    liveBadge: 'ताजा दर',
    mandi: 'मण्डी',
    rupees: 'रु',
    perKg: 'केजी',
    perMon: 'प्रति मन: रु',
    servicesTitle: 'मुख्य सेवाहरू',
    servicesSubtitle: 'अलैंची खेतीका लागि आधुनिक एआई उपकरणहरू',
    
    // Services cards
    diseaseTitle: 'रोग पहिचान',
    diseaseDesc: 'पातको फोटो खिचेर तत्काल एआई निदान, दागको अवस्थिति र उपचार पाउनुहोस्।',
    diseaseBadge: '९५.४% सही',
    voiceTitle: 'कृषि सल्लाहकार',
    voiceDesc: 'आफ्नो आवाजमा अलैंची खेतीबारे प्रश्न सोध्नुहोस् र तुरुन्तै जवाफ पाउनुहोस्।',
    voiceBadge: 'नेपाली अडियो',
    marketTitle: 'बजार भाउ',
    marketDesc: 'बिर्तामोड, ताप्लेजुङ, इलाम लगायत प्रमुख मण्डीहरूको दैनिक ताजा दरभाउ।',
    marketBadge: 'दैनिक अपडेट',
    syncTitle: 'अफलाइन सिंक',
    syncDesc: 'इन्टरनेट नहुँदा गरिएको निरीक्षण क्लाउडमा सुरक्षित गर्नुहोस्।',
    syncBadge: 'डबल मोड',
    
    // Disease detection screen
    detectionTitle: 'रोग पहिचान',
    detectionSubtitle: 'अलैंचीको पातको फोटो खिच्नुहोस्; एआईले रोगग्रस्त दाग चिन्ह लगाउनेछ',
    gallery: 'ग्यालरी',
    camera: 'क्यामेरा',
    quickSamplesHeader: '⚡ नमुना पातहरू:',
    sampleBlight: '🍂 पात डढुवा',
    sampleLeafSpot: '🍁 पात थोप्ले रोग',
    sampleHealthy: '🌿 स्वस्थ पात',
    tabAnnotated: '🎯 चिन्हित दाग',
    tabOriginal: '🌿 मूल फोटो',
    analyzeBtn: '🔍 रोग पत्ता लगाउनुहोस्',
    analyzing: 'एआई द्वारा रोगका दागहरू चिन्हित गरिँदैछ...',
    measuring: 'रोगको प्रकृति र फैलावट मापन हुँदैछ',
    diagnosisHeader: '🔬 परीक्षण नतिजा',
    metricLesions: 'रोगग्रस्त दागहरू',
    metricArea: 'फैलिएको भाग',
    metricConfidence: 'विश्वसनीयता',
    unitItems: 'वटा',
    boxesHeader: '🎯 फेला परेका रोगका दागहरू:',
    coords: 'अवस्थिति',
    to: 'देखि',
    treatmentHeader: '💊 उपचार तथा व्यवस्थापन',
    immediateSteps: 'तत्काल गर्नुपर्ने कामहरू:',
    preventionTips: 'बचावटका उपायहरू:',
    expectedRecovery: 'अनुमानित सुधार:',
    testAnother: '🔄 अर्को पात परीक्षण गर्नुहोस्',
    
    // Severity tags
    severe: 'गम्भीर',
    moderate: 'मध्यम',
    low: 'सामान्य',

    // Market Price Screen
    marketHeaderTitle: 'अलैंची बजार भाउ',
    marketHeaderSubtitle: 'नेपालका प्रमुख व्यापारिक केन्द्रहरूको दैनिक ताजा दर',
    allMarkets: 'सबै',
    perKilogram: 'प्रति किलोग्राम',
    perMonDetailed: 'प्रति मन • ४० केजी',
    marketDateLabel: 'मिति',
    marketRatesLoading: 'अलैंचीको ताजा बजार भाउ लोड हुँदैछ...',
    marketEmpty: 'यो मण्डीको दर उपलब्ध छैन।',
    marketOffline: 'ब्याकइन्डसँग सम्पर्क हुन सकेन, पछिल्लो दर देखाइएको छ।',
    districtLabel: 'जिल्ला',

    // Voice Query Screen
    voiceAdvisorScreenTitle: 'कृषि सल्लाहकार',
    voiceAdvisorScreenSubtitle: 'माइक्रोफोन थिच्नुहोस् र आफ्नो अलैंची खेती सम्बन्धी कुनै पनि जिज्ञासा सोध्नुहोस्।',
    tapToSpeak: 'नेपालीमा सोध्नुहोस्',
    stopRecording: 'रोक्नुहोस्',
    recordingActiveHint: 'आवाज रेकर्ड हुँदैछ... बोलिसकेपछि रोक्नुहोस्',
    voiceProcessingTitle: 'नेपाली आवाज प्रशोधन हुँदैछ...',
    voiceProcessingSub: 'कृषि विशेषज्ञको जवाफ तयार गरिँदैछ',
    yourQueryLabel: 'तपाईंको प्रश्न:',
    expertAdviceLabel: 'विशेषज्ञको सल्लाह:',
    listenVoice: 'जवाफ सुन्नुहोस्',
    pauseVoice: 'आवाज रोक्नुहोस्',
    micPermissionTitle: 'माइक्रोफोन अनुमति',
    micPermissionMsg: 'आवाज रेकर्ड गर्नका लागि कृपया माइक्रोफोनको अनुमति दिनुहोस्।',
    voiceErrorTitle: 'त्रुटि',
    voiceRecStartError: 'रेकर्डिङ सुरु गर्न सकिएन। कृपया पुनः प्रयास गर्नुहोस्।',
    voiceRecSaveError: 'रेकर्डिङ सुरक्षित गर्न सकिएन।',
    voiceConnErrorTitle: 'सम्पर्क हुन सकेन',
    voiceConnErrorMsg: 'ब्याकइन्ड सर्भरसँग आवाज विश्लेषण हुन सकेन।',
    voicePlayError: 'आवाज बजाउन सकिएन।',

    // Header Language Toggle
    langLabel: 'नेपाली',
  },
  en: {
    appTitle: 'KrishiMitra',
    homeSubtitle: 'Smart AI Companion for Nepali Cardamom Farmers',
    liveBadge: 'Live Spot Price',
    mandi: 'Mandi',
    rupees: 'NPR',
    perKg: 'kg',
    perMon: 'per Mon: NPR',
    servicesTitle: 'Smart Farm Services',
    servicesSubtitle: 'Modern computer vision & agronomic tools for large cardamom',
    
    // Services cards
    diseaseTitle: 'Disease Detection',
    diseaseDesc: 'Photograph leaf for instant pathology segmentation, lesion mapping & cures.',
    diseaseBadge: '95.4% Acc',
    voiceTitle: 'Agronomy Voice Expert',
    voiceDesc: 'Ask cardamom farming questions with your voice and receive instant guidance.',
    voiceBadge: 'Nepali Audio',
    marketTitle: 'Market Spot Rates',
    marketDesc: 'Daily verified auction prices from Birtamod, Taplejung, and Ilam trade centers.',
    marketBadge: 'Daily Live',
    syncTitle: 'Offline Batch Sync',
    syncDesc: 'Safely cache offline field inspections and sync when network connection returns.',
    syncBadge: 'Dual-Mode',
    
    // Disease detection screen
    detectionTitle: 'Disease Detection',
    detectionSubtitle: 'Upload or capture a leaf; AI detects, localizes lesions, and prescribes remedies',
    gallery: 'Gallery',
    camera: 'Camera',
    quickSamplesHeader: '⚡ Sample Leaves:',
    sampleBlight: '🍂 Leaf Blight',
    sampleLeafSpot: '🍁 Leaf Spot',
    sampleHealthy: '🌿 Healthy Leaf',
    tabAnnotated: '🎯 Detected Lesions',
    tabOriginal: '🌿 Original Photo',
    analyzeBtn: '🔍 Analyze Leaf',
    analyzing: 'AI is segmenting pathology lesions...',
    measuring: 'Measuring necrosis distribution and lesion severity',
    diagnosisHeader: '🔬 AI Diagnosis Result',
    metricLesions: 'Detected Lesions',
    metricArea: 'Infected Leaf Area',
    metricConfidence: 'AI Confidence',
    unitItems: 'boxes',
    boxesHeader: '🎯 Detected Pathology Bounding Boxes:',
    coords: 'Coordinates',
    to: 'to',
    treatmentHeader: '💊 Treatment & Management Protocol',
    immediateSteps: 'Immediate Action Steps:',
    preventionTips: 'Proactive Prevention Tips:',
    expectedRecovery: 'Expected Recovery Timeline:',
    testAnother: '🔄 Test Another Leaf',
    
    // Severity tags
    severe: 'Severe',
    moderate: 'Moderate',
    low: 'Healthy',

    // Market Price Screen
    marketHeaderTitle: 'Cardamom Market Rates',
    marketHeaderSubtitle: 'Daily verified auction rates from major trade centers',
    allMarkets: 'All',
    perKilogram: 'Per Kilogram',
    perMonDetailed: 'Per Mon • 40 kg',
    marketDateLabel: 'Date',
    marketRatesLoading: 'Loading latest cardamom market spot prices...',
    marketEmpty: 'No rates available for this trade center.',
    marketOffline: 'Offline mode: Showing cached market spot prices.',
    districtLabel: 'District',

    // Voice Query Screen
    voiceAdvisorScreenTitle: 'Agronomy Voice Expert',
    voiceAdvisorScreenSubtitle: 'Tap the microphone and ask any question about cardamom farming.',
    tapToSpeak: 'Tap to Speak',
    stopRecording: 'Stop Recording',
    recordingActiveHint: 'Recording audio... Tap stop when finished speaking',
    voiceProcessingTitle: 'Processing your voice query...',
    voiceProcessingSub: 'Synthesizing verified agronomic advice',
    yourQueryLabel: 'Your Query:',
    expertAdviceLabel: 'Expert Advice:',
    listenVoice: 'Listen to Voice Advice',
    pauseVoice: 'Pause Audio',
    micPermissionTitle: 'Microphone Required',
    micPermissionMsg: 'Please grant microphone access to record your voice.',
    voiceErrorTitle: 'Error',
    voiceRecStartError: 'Could not initialize microphone recording. Please retry.',
    voiceRecSaveError: 'Could not save voice recording.',
    voiceConnErrorTitle: 'Connection Failed',
    voiceConnErrorMsg: 'Could not connect to backend server for voice analysis.',
    voicePlayError: 'Could not play voice advice audio.',

    // Header Language Toggle
    langLabel: 'English',
  },
};

// Fallback English agronomic plans for diseases if backend only supplies Nepali
export const ENGLISH_TREATMENTS = {
  blight: {
    disease_name: 'Cardamom Leaf Blight',
    treatment_plan: [
      'Immediately prune and bury or burn infected, blighted leaves far away from the plantation.',
      'Spray Copper Oxychloride or 1% Bordeaux mixture at 2g per liter of water.',
      'For organic management, apply cold-pressed neem oil at 5ml per liter once weekly.',
      'Thin out overhead shade trees to improve air ventilation and sunlight penetration.',
      'Avoid applying chemical fertilizer or fungicides while leaf surfaces are wet.',
    ],
    prevention_tips: [
      'Proactively spray Bordeaux mixture before the onset of monsoon rains.',
      'Ensure deep drainage channels to prevent waterlogging around cardamom clumps.',
      'Plant only disease-free certified seedlings from registered nurseries.',
    ],
    expected_recovery: 'Fresh, healthy shoots will emerge within 2-3 weeks of active treatment.',
  },
  leaf_spot: {
    disease_name: 'Cardamom Phyllosticta Leaf Spot',
    treatment_plan: [
      'Prune and destroy leaves exhibiting small brown-yellow necrotic spots.',
      'Spray Mancozeb 75% WP at 2.5g per liter twice at a 10-12 day interval.',
      'Alternatively, apply Carbendazim 50% WP at 1g per liter of water for systematic control.',
      'Spray balanced micronutrients to enhance foliar vigor and disease resistance.',
    ],
    prevention_tips: [
      'Maintain balanced shade management with Alder or Siris trees for adequate sun.',
      'Avoid excessive high-nitrogen fertilizer usage which encourages fungal growth.',
      'Maintain appropriate plant clump spacing to avoid overcrowded canopies.',
    ],
    expected_recovery: 'Spot development halts on emerging foliage within 2 weeks.',
  },
  healthy: {
    disease_name: 'Healthy Cardamom Plant',
    treatment_plan: [
      'Your cardamom plant is healthy and exhibiting vigorous foliar growth.',
      'Continue routine weeding, organic mulching, and light moisture irrigation.',
      'Apply 5-10 kg of well-decomposed farmyard compost per clump annually.',
    ],
    prevention_tips: [
      'Regularly monitor plantation perimeter across seasonal transitions.',
      'Maintain 50% canopy shade using nitrogen-fixing Alder trees.',
    ],
    expected_recovery: 'Plant is healthy and capable of optimal seasonal capsule yield.',
  },
};

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState('ne'); // default: Nepali

  const toggleLanguage = () => {
    setLanguage((prev) => (prev === 'ne' ? 'en' : 'ne'));
  };

  const t = (key) => {
    const dict = TRANSLATIONS[language] || TRANSLATIONS.ne;
    return dict[key] || TRANSLATIONS.ne[key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, toggleLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    return {
      language: 'ne',
      setLanguage: () => {},
      toggleLanguage: () => {},
      t: (key) => TRANSLATIONS.ne[key] || key,
    };
  }
  return context;
}
