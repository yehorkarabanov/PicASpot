import React from 'react';
import { View } from 'react-native';
import { FlashList } from '@shopify/flash-list';
import { PostItem } from '@/components/feed/PostItem';
import { Post } from '@/lib/mockData';
import { getDistance } from '@/lib/map'; // Import the distance utility
import { Text } from '@/components/ui/text'; // For messages like "No nearby posts"

interface NearbyFeedListProps {
  posts: Post[];
  currentLocation: { latitude: number; longitude: number; };
  radius: number; // in km
  ListHeaderComponent?: React.ComponentType<any> | React.ReactElement | null;
  ListFooterComponent?: React.ComponentType<any> | React.ReactElement | null;
}

const NearbyFeedList: React.FC<NearbyFeedListProps> = ({ posts, currentLocation, radius, ListHeaderComponent, ListFooterComponent }) => {
  const nearbyPosts = posts.filter(post => {
    if (!post.latitude || !post.longitude) return false; // Post must have location data

    const distance = getDistance(
      currentLocation.latitude,
      currentLocation.longitude,
      post.latitude,
      post.longitude
    );
    return distance <= radius;
  });

  if (nearbyPosts.length === 0) {
    return (
      <View className="flex-1 items-center justify-center p-4">
        {ListHeaderComponent}
        <Text className="text-muted-foreground text-center mt-4">No posts found within {radius} km of your current location.</Text>
      </View>
    );
  }

  return (
    <View style={{ flex: 1 }}>
      <FlashList
        data={nearbyPosts}
        renderItem={({ item }) => <PostItem post={item} />}
        estimatedItemSize={200}
        keyExtractor={(item) => item.id}
        showsVerticalScrollIndicator={false}
        ListHeaderComponent={ListHeaderComponent}
        ListFooterComponent={ListFooterComponent}
      />
    </View>
  );
};

export { NearbyFeedList };
