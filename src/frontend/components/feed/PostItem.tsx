import React from 'react';
import { View, Image, TouchableOpacity } from 'react-native';
import { Text } from '@/components/ui/text';
import { Avatar } from '@/components/ui/Avatar';
import { Icon } from '@/components/ui/icon';
import { Heart, MessageSquare, Repeat } from 'lucide-react-native';
import { Post } from '@/lib/mockData';
import { useRouter } from 'expo-router';

interface PostItemProps {
  post: Post;
  isDetail?: boolean;
}

const PostItem: React.FC<PostItemProps> = ({ post, isDetail = false }) => {
  const router = useRouter();

  // Placeholder function for your future logic
  const handleGoToMark = () => {
    console.log('Go to mark logic triggered for post:', post.id);
  };

  const handlePressPost = () => {
    if (!isDetail) {
      router.push(`/post/${post.id}`);
    }
  };

  const handleAvatarPress = () => {
    router.push({
      pathname: '/media/avatar-preview',
      params: { uri: post.user.avatar }
    });
  };

  const handleUserPress = () => {
    router.push(`/user/${post.user.id}`);
  };

  return (
    <View className={`border-b border-border bg-background p-3 ${isDetail ? 'border-b-0' : ''}`}>
      <View className="flex-row">
        {/* 1. Left: Avatar */}
        <TouchableOpacity onPress={handleAvatarPress}>
           <Avatar source={post.user.avatar} size="md" className="mr-3" />
        </TouchableOpacity>

        {/* 2. Right: Content Column */}
        <View className="flex-1">
          {/* A. Header Row: User Info (Left) + Action Button (Right) */}
          <View className="flex-row items-start justify-between">
            {/* User Details */}
            <TouchableOpacity onPress={handleUserPress} className="mr-2 flex-1">
              <View className="flex-row flex-wrap items-center">
                <Text className="mr-1 font-semibold text-foreground">{post.user.name}</Text>
                <Text className="text-sm text-muted-foreground" numberOfLines={1}>
                  {post.user.username}
                </Text>
              </View>
              <Text className="mt-0.5 text-xs text-muted-foreground">{post.timestamp}</Text>
            </TouchableOpacity>

            {/* B. The New "Go to mark" Button */}
            <TouchableOpacity
              onPress={handleGoToMark}
              // Uses 'primary' color for visibility, or change to 'secondary' for subtle look
              className="rounded-full bg-primary px-3 py-1.5">
              <Text className="text-xs font-bold text-primary-foreground">Go to mark</Text>
            </TouchableOpacity>
          </View>

          {/* C. Post Body (Clickable only if not in detail view) */}
          <TouchableOpacity onPress={handlePressPost} activeOpacity={isDetail ? 1 : 0.8} disabled={isDetail}>
            <Text className="mt-2 text-base leading-5 text-foreground">{post.content}</Text>

            {/* D. Post Images (First one as cover) */}
            {post.images && post.images.length > 0 && (
              <View className="mt-3 relative">
                <Image
                  source={{ uri: post.images[0] }}
                  className="h-40 w-full rounded-lg bg-muted"
                  resizeMode="cover"
                />
                {post.images.length > 1 && (
                  <View className="absolute bottom-2 right-2 bg-black/60 px-2 py-1 rounded-md">
                    <Text className="text-white text-[10px] font-bold">1/{post.images.length}</Text>
                  </View>
                )}
              </View>
            )}
          </TouchableOpacity>

          {/* E. Action Bar (Likes, Comments, Shares) */}
          {/* Applied the 'gap-x' fix we discussed earlier */}
          <View className="mt-3 flex-row justify-between pr-4 pt-2">
            <TouchableOpacity className="flex-row items-center gap-x-1">
              <Icon as={Heart} className="text-muted-foreground" size={18} />
              <Text className="text-sm text-muted-foreground">{post.likes}</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              className="flex-row items-center gap-x-1" 
              onPress={handlePressPost}
              disabled={isDetail}
            >
              <Icon as={MessageSquare} className="text-muted-foreground" size={18} />
              <Text className="text-sm text-muted-foreground">{post.comments}</Text>
            </TouchableOpacity>

            <TouchableOpacity className="flex-row items-center gap-x-1">
              <Icon as={Repeat} className="text-muted-foreground" size={18} />
              <Text className="text-sm text-muted-foreground">{post.shares}</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </View>
  );
};

export { PostItem };
