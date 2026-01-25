import React, { useState, useEffect } from 'react';
import { View, TouchableOpacity, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as Location from 'expo-location';
import { useRouter } from 'expo-router';

import { FeedFilterBar, FeedType } from '@/components/feed/FeedFilterBar';
import { FollowingFeedList } from '@/components/feed/FollowingFeedList';
import { NearbyFeedList } from '@/components/feed/NearbyFeedList';
import { useAuth } from '@/contexts/AuthContext';
import { Avatar } from '@/components/ui/Avatar';
import { Button } from '@/components/ui/button';
import { Text } from '@/components/ui/text';
import { usePosts } from '@/hooks/usePosts'; // Custom hook for fetching posts

// Default location (Zurich) for prototyping
const DEFAULT_LOCATION = {
  latitude: 47.3768,
  longitude: 8.5417,
};

export default function FeedScreen() {
  const router = useRouter();
  const [activeFeed, setActiveFeed] = useState<FeedType>('following');
  const [radius, setRadius] = useState<number>(5);
  const [location, setLocation] = useState(DEFAULT_LOCATION);
  const { user } = useAuth();

  // Get User Location
  useEffect(() => {
    (async () => {
      try {
        let { status } = await Location.requestForegroundPermissionsAsync();
        if (status === 'granted') {
          let loc = await Location.getCurrentPositionAsync({});
          setLocation({
            latitude: loc.coords.latitude,
            longitude: loc.coords.longitude,
          });
        }
      } catch (error) {
        console.warn('Error getting location:', error);
      }
    })();
  }, []);

  // Fetch posts using the custom hook (API integration point)
  const { posts, isLoading, error } = usePosts({
    type: activeFeed,
    radius,
    userLocation: location
  });

  const CreatePostHeader = () => {
    return (
      <View className="p-4 bg-background border-b border-border">
        <View className="flex-row items-center space-x-5">
          <Avatar source={user?.avatar_url || 'https://github.com/shadcn.png'} size="md" />
          <TouchableOpacity 
            className="flex-1 ml-2"
            onPress={() => router.push('/create-post')}
          >
            <Text className="text-muted-foreground text-lg">What's happening?</Text>
          </TouchableOpacity>
          <Button size="sm" onPress={() => router.push('/create-post')}>
            <Text className="font-bold">Post</Text>
          </Button>
        </View>
      </View>
    );
  };

  const CaughtUpFooter = () => (
    <View className="py-8 items-center justify-center">
      <Text className="text-muted-foreground text-sm font-medium">You're all caught up!</Text>
    </View>
  );

  return (
    <SafeAreaView className="flex-1 bg-background" edges={['top']}>
      {/* 2. FIXED FILTER BAR (Tabs + Radius) */}
      <FeedFilterBar
        activeFeed={activeFeed}
        setActiveFeed={setActiveFeed}
        radius={radius}
        setRadius={setRadius}
        // ExtraHeaderComponent removed to allow scroll
      />

      {/* 3. SCROLLABLE CONTENT (Feed List) */}
      <View className="flex-1 bg-background">
        {isLoading ? (
           <View className="flex-1 justify-center items-center">
             <ActivityIndicator size="large" />
           </View>
        ) : activeFeed === 'following' ? (
          <FollowingFeedList 
            posts={posts} 
            ListHeaderComponent={<CreatePostHeader />}
            isLoading={isLoading}
          />
        ) : (
          <View style={{ flex: 1 }}>
            <NearbyFeedList
                posts={posts}
                ListHeaderComponent={<CreatePostHeader />}
                ListFooterComponent={<CaughtUpFooter />}
                isLoading={isLoading}
            />
          </View>
        )}
      </View>
    </SafeAreaView>
  );
}
