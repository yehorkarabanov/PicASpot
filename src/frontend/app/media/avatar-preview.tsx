import React from 'react';
import { View, Image, TouchableOpacity, StyleSheet, Share } from 'react-native';
import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import { BlurView } from 'expo-blur';
import { Icon } from '@/components/ui/icon';
import { X, Share2 } from 'lucide-react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Text } from '@/components/ui/text';

export default function AvatarPreview() {
  const router = useRouter();
  const { uri, username } = useLocalSearchParams<{ uri: string; username?: string }>();

  if (!uri) return null;

  const handleShare = async () => {
    try {
      await Share.share({
        message: `Check out ${username ? `@${username}'s` : 'this'} avatar on PicASpot!`,
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
            contentStyle: { backgroundColor: 'transparent' }
          }} 
       />
      
      <BlurView intensity={40} style={styles.absolute} tint="systemThinMaterialDark" />
      
      <TouchableOpacity 
        style={styles.absolute} 
        activeOpacity={1} 
        onPress={() => router.back()}
      />

      <SafeAreaView className="flex-1 justify-center items-center" pointerEvents="box-none">
        <View 
            className="w-[94%] h-[85%] bg-card rounded-2xl overflow-hidden shadow-2xl border border-border"
            style={styles.cardShadow}
        >
            <View className="flex-row justify-between items-center px-4 py-3 bg-card/95 absolute top-0 left-0 right-0 z-10 border-b border-border/10">
                <View className="w-10" />

                <Text className="text-sm font-semibold text-foreground" numberOfLines={1}>
                  {username ? `@${username}` : 'Avatar'}
                </Text>

                <TouchableOpacity 
                    onPress={() => router.back()} 
                    className="p-2 rounded-full bg-secondary/80"
                >
                    <Icon as={X} size={20} className="text-foreground" />
                </TouchableOpacity>
            </View>

            <View className="flex-1 bg-black/5 justify-center items-center">
                 <Image 
                    source={{ uri }} 
                    className="w-full h-full"
                    resizeMode="contain" 
                  />
            </View>

            <View className="flex-row justify-center items-center p-4 bg-card border-t border-border/10 gap-6">
                <TouchableOpacity 
                  className="flex-row items-center gap-2 bg-primary px-6 py-2 rounded-full"
                  onPress={handleShare}
                >
                    <Icon as={Share2} size={18} className="text-primary-foreground" />
                    <Text className="text-primary-foreground font-medium">Share</Text>
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
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 10,
    },
    shadowOpacity: 0.3,
    shadowRadius: 20,
    elevation: 10,
  }
});
