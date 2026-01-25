import React from 'react';
import { View, Image, TouchableOpacity, StyleSheet, Dimensions } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { BlurView } from 'expo-blur';
import { Icon } from '@/components/ui/icon';
import { X } from 'lucide-react-native';

const { width } = Dimensions.get('window');

export default function AvatarPreview() {
  const router = useRouter();
  const { uri } = useLocalSearchParams<{ uri: string }>();

  if (!uri) return null;

  return (
    <View style={styles.container}>
      <BlurView intensity={20} style={styles.absolute} tint="dark" />
      
      <TouchableOpacity 
        style={styles.absolute} 
        activeOpacity={1} 
        onPress={() => router.back()}
      />

      <View style={styles.content}>
        <Image 
          source={{ uri }} 
          style={styles.image} 
          resizeMode="cover" 
        />
        
        <TouchableOpacity 
          style={styles.closeButton} 
          onPress={() => router.back()}
        >
          <Icon as={X} size={24} color="white" />
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.3)', // Slight dark overlay
  },
  absolute: {
    position: 'absolute',
    top: 0,
    left: 0,
    bottom: 0,
    right: 0,
  },
  content: {
    position: 'relative',
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  image: {
    width: width * 0.8,
    height: width * 0.8,
    borderRadius: (width * 0.8) / 2,
  },
  closeButton: {
    position: 'absolute',
    top: -40,
    right: 0,
    padding: 8,
  },
});
