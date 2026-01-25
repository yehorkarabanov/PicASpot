import React, { useState, useEffect, useMemo } from 'react';
import { View, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as Location from 'expo-location';
import { useRouter } from 'expo-router';

import { MOCK_FEED_POSTS, Post } from '@/lib/mockData';
import { FeedFilterBar, FeedType } from '@/components/feed/FeedFilterBar';
import { FollowingFeedList } from '@/components/feed/FollowingFeedList';
import { NearbyFeedList } from '@/components/feed/NearbyFeedList';
import { useLandmarks } from '@/contexts/LandmarkContext';
import { useAuth } from '@/contexts/AuthContext';
import { Avatar } from '@/components/ui/Avatar';
import { Button } from '@/components/ui/button';
import { Text } from '@/components/ui/text';

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
  
  const { landmarks, fetchNearbyLandmarks, isLoading } = useLandmarks();
  const { isAuthenticated, user } = useAuth();

  // Generate a large list of mock posts to simulate infinite scroll
  const LARGE_MOCK_POSTS = useMemo(() => {
    return Array.from({ length: 100 }).flatMap((_, i) => 
      MOCK_FEED_POSTS.map(post => ({
        ...post,
        id: `${post.id}-${i}`, // Ensure unique IDs
      }))
    );
  }, []);

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

  // Fetch landmarks when activeFeed is nearby or params change
  // MOCK MODE: Disabled fetching to show mock data
  /*
  useEffect(() => {
    if (activeFeed === 'nearby' && isAuthenticated) {
      // Radius in meters
      fetchNearbyLandmarks(location.latitude, location.longitude, radius * 1000);
    }
  }, [activeFeed, radius, location, fetchNearbyLandmarks, isAuthenticated]);
  */

  // Convert landmarks to posts
  // MOCK MODE: Use LARGE_MOCK_POSTS directly
  const nearbyPosts: Post[] = LARGE_MOCK_POSTS;

  console.log('Rendering FeedScreen', { activeFeed, postsCount: nearbyPosts.length, isAuthenticated });

  const CreatePostHeader = () => {
    return (
      <View className="p-4 border-b border-border bg-background">
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
      {/* 1. FIXED HEADER (Input + Tabs) */}
      <FeedFilterBar
        activeFeed={activeFeed}
        setActiveFeed={setActiveFeed}
        radius={radius}
        setRadius={setRadius}
      />

      {/* 2. SCROLLABLE CONTENT (Feed List) */}
      <View className="flex-1 bg-background">
        {activeFeed === 'following' ? (
          <FollowingFeedList 
            posts={LARGE_MOCK_POSTS} 
            ListHeaderComponent={<CreatePostHeader />}
          />
        ) : (
          <View style={{ flex: 1 }}>
            <NearbyFeedList
                posts={nearbyPosts}
                currentLocation={location}
                radius={radius}
                ListFooterComponent={<CaughtUpFooter />}
            />
          </View>
        )}
      </View>
    </SafeAreaView>
  );
}
