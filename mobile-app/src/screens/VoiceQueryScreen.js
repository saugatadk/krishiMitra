import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  ScrollView,
  Alert,
  Platform,
} from 'react-native';
import {
  useAudioRecorder,
  RecordingPresets,
  requestRecordingPermissionsAsync,
  createAudioPlayer,
} from 'expo-audio';
import { sendVoiceQuery } from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import LanguageToggle from '../components/LanguageToggle';

export default function VoiceQueryScreen() {
  const { t, language } = useLanguage();
  const recorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
  const [player, setPlayer] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [loading, setLoading] = useState(false);
  const [queryText, setQueryText] = useState('');
  const [responseText, setResponseText] = useState('');
  const [responseAudioUrl, setResponseAudioUrl] = useState(null);

  const timerRef = useRef(null);

  useEffect(() => {
    // Clean up audio player on unmount
    return () => {
      if (player) {
        try {
          if (typeof player.pause === 'function') player.pause();
          if (typeof player.release === 'function') player.release();
        } catch (e) {}
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [player]);

  async function startRecording() {
    try {
      // 1. Request microphone permissions
      const permission = await requestRecordingPermissionsAsync();
      if (!permission.granted) {
        Alert.alert(t('micPermissionTitle'), t('micPermissionMsg'));
        return;
      }

      // 2. Prepare & Start Recording
      await recorder.prepareToRecordAsync();
      recorder.record();
      setIsRecording(true);
      setRecordingDuration(0);

      // Start duration ticker
      timerRef.current = setInterval(() => {
        setRecordingDuration((prev) => prev + 1);
      }, 1000);
    } catch (err) {
      console.error('Failed to start recording', err);
      Alert.alert(t('voiceErrorTitle'), t('voiceRecStartError'));
    }
  }

  async function stopRecording() {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    setIsRecording(false);
    try {
      await recorder.stop();
      const uri = recorder.uri;

      if (uri) {
        handleUploadAudio(uri);
      }
    } catch (err) {
      console.error('Failed to stop recording', err);
      Alert.alert(t('voiceErrorTitle'), t('voiceRecSaveError'));
    }
  }

  const handleUploadAudio = async (audioUri) => {
    setLoading(true);
    setQueryText('');
    setResponseText('');
    setResponseAudioUrl(null);

    // Stop any existing player
    if (player) {
      try {
        if (typeof player.pause === 'function') player.pause();
        if (typeof player.release === 'function') player.release();
      } catch (e) {}
      setPlayer(null);
      setIsPlaying(false);
    }

    try {
      const data = await sendVoiceQuery(audioUri);
      setQueryText(data.query_text);
      setResponseText(data.response);
      if (data.response_audio_url) {
        setResponseAudioUrl(data.response_audio_url);
      }
    } catch (error) {
      console.error('Audio upload error:', error);
      Alert.alert(t('voiceConnErrorTitle'), t('voiceConnErrorMsg'));
    } finally {
      setLoading(false);
    }
  };

  const playVoiceResponse = async () => {
    if (!responseAudioUrl) return;

    try {
      if (player) {
        if (isPlaying) {
          player.pause();
          setIsPlaying(false);
        } else {
          player.play();
          setIsPlaying(true);
        }
        return;
      }

      // Web fallback with HTML5 Audio
      if (Platform.OS === 'web' && typeof window !== 'undefined' && window.Audio) {
        const htmlAudio = new window.Audio(responseAudioUrl);
        htmlAudio.onended = () => setIsPlaying(false);
        htmlAudio.play();
        setPlayer(htmlAudio);
        setIsPlaying(true);
        return;
      }

      // Native SDK 58 AudioPlayer
      const newPlayer = createAudioPlayer({ uri: responseAudioUrl });
      newPlayer.play();
      setPlayer(newPlayer);
      setIsPlaying(true);

      newPlayer.addListener('playbackStatusUpdate', (status) => {
        if (status.playbackState === 'finished' || (status.duration > 0 && status.currentTime >= status.duration)) {
          setIsPlaying(false);
        }
      });
    } catch (error) {
      console.error('Audio playback error:', error);
      Alert.alert(t('voiceErrorTitle'), t('voicePlayError'));
    }
  };

  const formatSeconds = (sec) => {
    const mins = Math.floor(sec / 60);
    const secs = sec % 60;
    return `${mins < 10 ? '0' : ''}${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>{t('voiceAdvisorScreenTitle')}</Text>
      <Text style={styles.instructions}>{t('voiceAdvisorScreenSubtitle')}</Text>

      {/* Language Toggle */}
      <LanguageToggle style={{ marginBottom: 16 }} />

      {/* Recording Microphone Action */}
      <View style={styles.micContainer}>
        <TouchableOpacity
          style={[styles.micButton, isRecording && styles.micButtonRecording]}
          onPress={isRecording ? stopRecording : startRecording}
          activeOpacity={0.8}
        >
          <Text style={styles.micIcon}>{isRecording ? '⏹️' : '🎤'}</Text>
          <Text style={styles.micText}>
            {isRecording ? t('stopRecording') : t('tapToSpeak')}
          </Text>
          {isRecording && (
            <Text style={styles.timerText}>{formatSeconds(recordingDuration)}</Text>
          )}
        </TouchableOpacity>
        {isRecording && (
          <Text style={styles.recordingHint}>{t('recordingActiveHint')}</Text>
        )}
      </View>

      {/* Processing Loader */}
      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#2e7d32" />
          <Text style={styles.loadingText}>{t('voiceProcessingTitle')}</Text>
          <Text style={styles.loadingSubtext}>{t('voiceProcessingSub')}</Text>
        </View>
      )}

      {/* Results Box */}
      {queryText ? (
        <View style={styles.chatContainer}>
          {/* User's Transcribed Query */}
          <View style={styles.userQueryBox}>
            <Text style={styles.label}>{t('yourQueryLabel')}</Text>
            <Text style={styles.queryText}>"{queryText}"</Text>
          </View>

          <View style={styles.divider} />

          {/* Expert Answer */}
          <View style={styles.expertAnswerBox}>
            <Text style={styles.label}>{t('expertAdviceLabel')}</Text>
            <Text style={styles.responseText}>{responseText}</Text>

            {/* Audio Playback Button (For Illiterate Farmers) */}
            {responseAudioUrl && (
              <TouchableOpacity
                style={[styles.audioPlayButton, isPlaying && styles.audioPlayingButton]}
                onPress={playVoiceResponse}
                activeOpacity={0.8}
              >
                <Text style={styles.playIcon}>{isPlaying ? '⏸️' : '🔊'}</Text>
                <Text style={styles.audioPlayText}>
                  {isPlaying ? t('pauseVoice') : t('listenVoice')}
                </Text>
              </TouchableOpacity>
            )}
          </View>
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
    paddingBottom: 100,
    ...(Platform.OS === 'web'
      ? {
          height: '100%',
          overflowY: 'auto',
          WebkitOverflowScrolling: 'touch',
        }
      : {}),
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#1b5e20',
    textAlign: 'center',
    marginBottom: 6,
  },
  instructions: {
    fontSize: 14,
    color: '#555',
    textAlign: 'center',
    lineHeight: 20,
    marginBottom: 8,
  },
  micContainer: {
    alignItems: 'center',
    marginVertical: 24,
  },
  micButton: {
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: '#2e7d32',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 8,
    shadowColor: '#2e7d32',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.35,
    shadowRadius: 10,
  },
  micButtonRecording: {
    backgroundColor: '#c62828',
    shadowColor: '#c62828',
  },
  micIcon: {
    fontSize: 44,
    marginBottom: 4,
  },
  micText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 12,
    textAlign: 'center',
    paddingHorizontal: 8,
  },
  timerText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '600',
    marginTop: 2,
  },
  recordingHint: {
    marginTop: 12,
    fontSize: 13,
    color: '#c62828',
    fontWeight: '500',
  },
  loadingContainer: {
    alignItems: 'center',
    marginVertical: 20,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 15,
    color: '#2e7d32',
    fontWeight: 'bold',
  },
  loadingSubtext: {
    fontSize: 12,
    color: '#777',
    marginTop: 4,
  },
  chatContainer: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 6,
    borderWidth: 1,
    borderColor: '#e0f2f1',
  },
  userQueryBox: {
    marginBottom: 12,
  },
  label: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#1b5e20',
    marginBottom: 4,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  queryText: {
    fontSize: 15,
    fontStyle: 'italic',
    color: '#333',
    lineHeight: 22,
  },
  divider: {
    height: 1,
    backgroundColor: '#e0e0e0',
    marginVertical: 12,
  },
  expertAnswerBox: {
    marginTop: 4,
  },
  responseText: {
    fontSize: 15,
    color: '#222',
    lineHeight: 24,
    marginBottom: 16,
  },
  audioPlayButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#e8f5e9',
    paddingVertical: 12,
    paddingHorizontal: 18,
    borderRadius: 12,
    borderWidth: 1.5,
    borderColor: '#81c784',
    alignSelf: 'flex-start',
  },
  audioPlayingButton: {
    backgroundColor: '#ffebee',
    borderColor: '#e57373',
  },
  playIcon: {
    fontSize: 18,
    marginRight: 8,
  },
  audioPlayText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1b5e20',
  },
});
