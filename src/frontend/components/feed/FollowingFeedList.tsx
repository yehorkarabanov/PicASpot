import React from 'react';
import { View } from 'react-native';
import { FlashList } from '@shopify/flash-list';
import { PostItem } from '@/components/feed/PostItem';
import { Post } from '@/lib/mockData';

interface FollowingFeedListProps {
  posts: Post[];
  ListHeaderComponent?: React.ComponentType<any> | React.ReactElement | null;
}

const FollowingFeedList: React.FC<FollowingFeedListProps> = ({ posts, ListHeaderComponent }) => {
  const followingPosts = posts.filter(post => post.user.isFollowing);

  return (
    <View style={{ flex: 1 }}>
      <FlashList
        data={followingPosts}
        renderItem={({ item }) => <PostItem post={item} />}
        estimatedItemSize={200}
        keyExtractor={(item) => item.id}
        showsVerticalScrollIndicator={false}
        ListHeaderComponent={ListHeaderComponent}
      />
    </View>
  );
};

export { FollowingFeedList };
