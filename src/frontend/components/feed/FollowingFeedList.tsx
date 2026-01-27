import React from 'react';
import { View } from 'react-native';
import { FlashList } from '@shopify/flash-list';
import { PostItem } from '@/components/feed/PostItem';
import { Post } from '@/lib/mockData';
import { Text } from '@/components/ui/text';

interface FollowingFeedListProps {
  posts: Post[];
  isLoading?: boolean;
  ListHeaderComponent?: React.ComponentType<any> | React.ReactElement | null;
}

const FollowingFeedList: React.FC<FollowingFeedListProps> = ({ posts, isLoading, ListHeaderComponent }) => {
  
  if (!isLoading && posts.length === 0) {
    return (
       <View style={{ flex: 1 }}>
        {ListHeaderComponent}
        <View className="flex-1 items-center justify-center p-4">
          <Text className="text-muted-foreground text-center mt-4">Follow users to see their posts here!</Text>
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
      />
    </View>
  );
};

export { FollowingFeedList };
