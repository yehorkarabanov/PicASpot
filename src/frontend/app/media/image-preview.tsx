import React from 'react';
import { View, Image, TouchableOpacity, StyleSheet, Platform, Share } from 'react-native';
import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import { BlurView } from 'expo-blur';
import { Icon } from '@/components/ui/icon';
import { X, Share2 } from 'lucide-react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Text } from '@/components/ui/text';

export default function ImagePreview() {
  const router = useRouter();
  const { uri } = useLocalSearchParams<{ uri: string }>();

  if (!uri) return null;

  const handleShare = async () => {
    try {
      await Share.share({
        message: 'Check out this image from PicASpot!',
        url: uri,
      });
    } catch (error: any) {
      console.error(error.message);
    }
  };

  return (
    <View style={styles.container}>
      <Stack.Screen
        options={{
          headerShown: false,
          presentation: 'transparentModal',
          animation: 'fade',
          contentStyle: { backgroundColor: 'transparent' },
        }}
      />

      {}
      <BlurView intensity={40} style={styles.absolute} tint="systemThinMaterialDark" />

      {}
      <TouchableOpacity style={styles.absolute} activeOpacity={1} onPress={() => router.back()} />

      <SafeAreaView className="flex-1 items-center justify-center" pointerEvents="box-none">
        {}
        <View
          className="h-[85%] w-[94%] overflow-hidden rounded-2xl border border-border bg-card shadow-2xl"
          style={styles.cardShadow}>
          {}
          <View className="absolute left-0 right-0 top-0 z-10 flex-row items-center justify-between border-b border-border/10 bg-card/95 px-4 py-3">
            <View className="w-10" />

            <Text className="text-sm font-semibold text-muted-foreground">Preview</Text>

            <TouchableOpacity
              onPress={() => router.back()}
              className="rounded-full bg-secondary/80 p-2">
              <Icon as={X} size={20} className="text-foreground" />
            </TouchableOpacity>
          </View>

          {}
          <View className="flex-1 items-center justify-center bg-black/5">
            <Image source={{ uri }} className="h-full w-full" resizeMode="contain" />
          </View>

          {}
          <View className="flex-row items-center justify-center gap-6 border-t border-border/10 bg-card p-4">
            <TouchableOpacity
              className="flex-row items-center gap-2 rounded-full bg-primary px-6 py-2"
              onPress={handleShare}>
              <Icon as={Share2} size={18} className="text-primary-foreground" />
              <Text className="font-medium text-primary-foreground">Share</Text>
            </TouchableOpacity>
          </View>
        </View>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'transparent',
  },
  absolute: {
    position: 'absolute',
    top: 0,
    left: 0,
    bottom: 0,
    right: 0,
  },
  cardShadow: {
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 10,
    },
    shadowOpacity: 0.3,
    shadowRadius: 20,
    elevation: 10,
  },
});
