import React, { useState } from 'react';
import {
  View,
  Image,
  TouchableOpacity,
  ScrollView,
  TextInput,
  Alert,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
} from 'react-native';
import { Stack, useRouter } from 'expo-router';
import * as ImagePicker from 'expo-image-picker';
import { Image as ImageIcon, MapPin, X } from 'lucide-react-native';
import { Button } from '@/components/ui/button';
import { Text } from '@/components/ui/text';
import { Icon } from '@/components/ui/icon';
import { useAuth } from '@/contexts/AuthContext';
import { Avatar } from '@/components/ui/Avatar';
import { cn } from '@/lib/utils';
import { BlurView } from 'expo-blur';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function CreatePostScreen() {
  const router = useRouter();
  const { user } = useAuth();
  const [content, setContent] = useState('');
  const [image, setImage] = useState<string | null>(null);
  const [hasMark, setHasMark] = useState(false);

  const pickImage = async () => {
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

  const toggleMark = () => {
    setHasMark(!hasMark);
  };

  const handlePost = async () => {
    console.log('Posting:', { content, image, hasMark });
    router.back();
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
      <TouchableOpacity
        style={styles.absolute}
        activeOpacity={1}
        onPress={() => {
          if (content.trim() || image) {
            Alert.alert(
              'Discard Post?',
              'You have unsaved changes. Are you sure you want to discard them?',
              [
                { text: 'Keep Editing', style: 'cancel' },
                { text: 'Discard', style: 'destructive', onPress: () => router.back() },
              ]
            );
          } else {
            router.back();
          }
        }}
      />

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        className="flex-1 items-center justify-center"
        pointerEvents="box-none">
        <View
          className="max-h-[85%] w-[94%] overflow-hidden rounded-2xl border border-border bg-card shadow-2xl"
          style={styles.cardShadow}>
          {}
          <View className="flex-row items-center justify-between border-b border-border/10 bg-card/95 px-4 py-3">
            <Button variant="ghost" size="sm" onPress={() => router.back()} className="px-2">
              <Text className="text-base font-normal text-muted-foreground">Cancel</Text>
            </Button>

            <Text className="text-base font-semibold text-foreground">New Post</Text>

            <Button
              size="sm"
              onPress={handlePost}
              disabled={!content.trim() && !image}
              className="h-8 rounded-full px-4">
              <Text className="font-bold text-primary-foreground">Post</Text>
            </Button>
          </View>

          {}
          <ScrollView className="px-4 pt-4">
            <View className="flex-row gap-3">
              <Avatar source={user?.avatar_url || 'https://github.com/shadcn.png'} size="md" />
              <View className="flex-1">
                <TextInput
                  className="min-h-[80px] pt-1 text-justify text-lg leading-6 text-foreground"
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

            {}
            <View className="mb-20 ml-[50px] mt-2 gap-3">
              {image && (
                <View className="relative overflow-hidden rounded-2xl border border-border">
                  <Image
                    source={{ uri: image }}
                    className="aspect-video w-full"
                    resizeMode="cover"
                  />
                  <TouchableOpacity
                    className="absolute right-2 top-2 rounded-full bg-black/60 p-1.5"
                    onPress={() => setImage(null)}>
                    <Icon as={X} size={16} color="white" />
                  </TouchableOpacity>
                </View>
              )}

              {hasMark && (
                <View className="flex-row items-center self-start rounded-xl border border-border bg-secondary/30 px-3 py-2">
                  <Icon as={MapPin} size={16} className="mr-2 text-primary" />
                  <Text className="font-medium text-foreground">Current Location Attached</Text>
                  <TouchableOpacity
                    className="ml-2 rounded-full bg-muted-foreground/20 p-0.5"
                    onPress={() => setHasMark(false)}>
                    <Icon as={X} size={14} className="text-foreground" />
                  </TouchableOpacity>
                </View>
              )}
            </View>
          </ScrollView>

          {}
          <View className="flex-row items-center gap-2 border-t border-border bg-card p-3">
            <Button variant="ghost" size="icon" onPress={pickImage} className="rounded-full">
              <Icon as={ImageIcon} size={24} className="text-primary" />
            </Button>

            <Button
              variant={hasMark ? 'secondary' : 'ghost'}
              size="sm"
              onPress={toggleMark}
              className={cn('flex-row gap-2 rounded-full', hasMark && 'bg-primary/10')}>
              <Icon
                as={MapPin}
                size={20}
                className={cn('text-primary', hasMark && 'text-primary')}
              />
              <Text
                className={cn(
                  'font-medium text-primary',
                  !hasMark && 'font-normal text-foreground'
                )}>
                Attach Mark
              </Text>
            </Button>
          </View>
        </View>
      </KeyboardAvoidingView>
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
