import React from 'react';
import { View } from 'react-native';
import { FlashList } from '@shopify/flash-list';
import { PostItem } from '@/components/feed/PostItem';
import { Post } from '@/lib/mockData';
import { Text } from '@/components/ui/text';

interface NearbyFeedListProps {
  posts: Post[];
  ListHeaderComponent?: React.ComponentType<any> | React.ReactElement | null;
  ListFooterComponent?: React.ComponentType<any> | React.ReactElement | null;
}

const NearbyFeedList: React.FC<NearbyFeedListProps> = ({
  posts,
  isLoading,
  ListHeaderComponent,
  ListFooterComponent,
}) => {
  if (!isLoading && posts.length === 0) {
    return (
      <View style={{ flex: 1 }}>
        {ListHeaderComponent}
        <View className="flex-1 items-center justify-center p-4">
          <Text className="mt-4 text-center text-muted-foreground">No nearby posts found.</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={{ flex: 1 }}>
      <FlashList
        data={posts}
        renderItem={({ item }) => <PostItem post={item} />}
        estimatedItemSize={400}
        keyExtractor={(item) => item.id}
        showsVerticalScrollIndicator={false}
        ListHeaderComponent={ListHeaderComponent}
        ListFooterComponent={ListFooterComponent}
      />
    </View>
  );
};

export { NearbyFeedList };
