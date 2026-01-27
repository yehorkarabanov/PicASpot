import React, { useState, useEffect } from 'react';
import { View, TouchableOpacity, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as Location from 'expo-location';
import { useRouter } from 'expo-router';

import { FeedFilterBar, FeedType } from '@/components/feed/FeedFilterBar';
import { RadiusSelector } from '@/components/feed/RadiusSelector';
import { FollowingFeedList } from '@/components/feed/FollowingFeedList';
import { NearbyFeedList } from '@/components/feed/NearbyFeedList';
import { useAuth } from '@/contexts/AuthContext';
import { Avatar } from '@/components/ui/Avatar';
import { Button } from '@/components/ui/button';
import { Text } from '@/components/ui/text';
import { usePosts } from '@/hooks/usePosts';

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

  const { posts, isLoading, error } = usePosts({
    type: activeFeed,
    radius,
    userLocation: location,
  });

  const CreatePostHeader = () => {
    return (
      <View className="border-b border-border bg-background p-4">
        <View className="flex-row items-center space-x-5">
          <Avatar source={user?.avatar_url || 'https://github.com/shadcn.png'} size="md" />
          <TouchableOpacity className="ml-2 flex-1" onPress={() => router.push('/create-post')}>
            <Text className="text-lg text-muted-foreground">What's happening?</Text>
          </TouchableOpacity>
          <Button size="sm" onPress={() => router.push('/create-post')}>
            <Text className="font-bold">Post</Text>
          </Button>
        </View>
      </View>
    );
  };

  const NearbyHeader = () => {
    return (
      <View>
        <CreatePostHeader />
        <RadiusSelector radius={radius} setRadius={setRadius} />
      </View>
    );
  };

  const CaughtUpFooter = () => (
    <View className="items-center justify-center py-8">
      <Text className="text-sm font-medium text-muted-foreground">You're all caught up!</Text>
    </View>
  );

  return (
    <SafeAreaView className="flex-1 bg-background" edges={['top']}>
      {}
      <FeedFilterBar activeFeed={activeFeed} setActiveFeed={setActiveFeed} />

      {}
      <View className="flex-1 bg-background">
        {isLoading ? (
          <View className="flex-1 items-center justify-center">
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
              ListHeaderComponent={<NearbyHeader />}
              ListFooterComponent={<CaughtUpFooter />}
              isLoading={isLoading}
            />
          </View>
        )}
      </View>
    </SafeAreaView>
  );
}
