import React, { useState } from 'react';
import { View, Image, TouchableOpacity, ScrollView, TextInput, Alert } from 'react-native';
import { Stack, useRouter } from 'expo-router';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import { Button } from '@/components/ui/button';
import { Text } from '@/components/ui/text';
import { useAuth } from '@/contexts/AuthContext';
import { Avatar } from '@/components/ui/Avatar';

export default function CreatePostScreen() {
  const router = useRouter();
  const { user } = useAuth();
  const [content, setContent] = useState('');
  const [image, setImage] = useState<string | null>(null);

  const pickImage = async () => {
    // Request permission first
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Sorry, we need camera roll permissions to make this work!');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 0.8,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
    }
  };

  const handlePost = async () => {
    // Here you would typically upload the image and create the post via API
    // For now, we'll just log it and go back
    console.log('Posting:', { content, image });
    router.back();
  };

  return (
    <View className="flex-1 bg-background">
      <Stack.Screen 
        options={{
          title: 'Create Post',
          headerLeft: () => (
            <TouchableOpacity onPress={() => router.back()}>
              <Text className="text-foreground text-lg">Cancel</Text>
            </TouchableOpacity>
          ),
          headerRight: () => (
            <Button 
              size="sm" 
              onPress={handlePost} 
              disabled={!content.trim() && !image}
              className="px-4"
            >
              <Text className="font-bold text-primary-foreground">Post</Text>
            </Button>
          ),
          presentation: 'modal',
        }} 
      />
      
      <ScrollView className="flex-1 p-4">
        <View className="flex-row space-x-3">
          <Avatar source={user?.avatar_url || 'https://github.com/shadcn.png'} size="md" />
          <View className="flex-1">
             <TextInput
                className="text-lg text-foreground min-h-[100px] text-justify pt-2"
                multiline
                placeholder="What's happening?"
                placeholderTextColor="#666"
                value={content}
                onChangeText={setContent}
                autoFocus
                textAlignVertical="top"
              />
          </View>
        </View>

        {image && (
          <View className="mt-4 relative">
             <Image source={{ uri: image }} className="w-full h-64 rounded-xl" resizeMode="cover" />
             <TouchableOpacity 
                className="absolute top-2 right-2 bg-black/50 p-1 rounded-full"
                onPress={() => setImage(null)}
             >
               <Ionicons name="close" size={20} color="white" />
             </TouchableOpacity>
          </View>
        )}
      </ScrollView>

      <View className="p-4 border-t border-border bg-background flex-row items-center justify-between">
        <TouchableOpacity onPress={pickImage} className="p-2">
           <Ionicons name="image-outline" size={28} color="#007AFF" />
        </TouchableOpacity>
      </View>
    </View>
  );
}
