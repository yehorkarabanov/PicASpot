import React, { useState, useRef } from 'react';
import { View, Image, TouchableOpacity, Pressable, Share, Alert } from 'react-native';
import { Text } from '@/components/ui/text';
import { Avatar } from '@/components/ui/Avatar';
import { Icon } from '@/components/ui/icon';
import { Heart, MessageSquare, Share2 } from 'lucide-react-native';
import { Post } from '@/lib/mockData';
import { useRouter } from 'expo-router';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withSpring, 
  withSequence, 
  withDelay 
} from 'react-native-reanimated';

interface PostItemProps {
  post: Post;
  isDetail?: boolean;
}

const PostItem: React.FC<PostItemProps> = ({ post, isDetail = false }) => {
  const router = useRouter();
  const [isLiked, setIsLiked] = useState(false);
  const [likesCount, setLikesCount] = useState(post.likes);
  
  // Animation state
  const scale = useSharedValue(0);
  const lastTap = useRef<number>(0);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const handleGoToMark = () => {
    console.log('Go to mark logic triggered for post:', post.id);
  };

  const handlePressPost = () => {
    if (!isDetail) {
      router.push(`/post/${post.id}`);
    }
  };

  const handleShare = () => {
    Alert.alert(
      'Share Post',
      'Choose how you want to share this post',
      [
        {
          text: 'Repost',
          onPress: () => {
             // TODO: Implement internal repost logic
             console.log('Reposted internally');
             Alert.alert('Success', 'Post reposted to your feed!');
          }
        },
        {
          text: 'Share via...',
          onPress: async () => {
            try {
              await Share.share({
                message: `Check out this post by ${post.user.name} on PicASpot!`,
                url: post.images?.[0], 
              });
            } catch (error: any) {
              console.error(error.message);
            }
          }
        },
        {
          text: 'Cancel',
          style: 'cancel',
        },
      ]
    );
  };

  const animatedHeartStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: scale.value > 0 ? 1 : 0,
  }));

  const triggerLikeAnimation = () => {
    scale.value = withSequence(
      withSpring(1.2),
      withDelay(500, withSpring(0))
    );
  };

  const toggleLike = () => {
    if (!isLiked) {
      setLikesCount(prev => prev + 1);
      setIsLiked(true);
      triggerLikeAnimation();
    } else {
      setLikesCount(prev => prev - 1);
      setIsLiked(false);
    }
  };

  const handleDoubleTap = () => {
    const now = Date.now();
    const DOUBLE_TAP_DELAY = 300;

    if (lastTap.current && now - lastTap.current < DOUBLE_TAP_DELAY) {
      // DOUBLE TAP DETECTED -> LIKE
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
      
      lastTap.current = 0; 

      if (!isLiked) {
        toggleLike();
      } else {
        triggerLikeAnimation();
      }
    } else {
      // SINGLE TAP DETECTED -> OPEN IMAGE PREVIEW
      lastTap.current = now;
      
      timerRef.current = setTimeout(() => {
           // Open image preview instead of post details
           if (post.images && post.images.length > 0) {
             router.push({
               pathname: '/media/image-preview',
               params: { uri: post.images[0] }
             });
           }
           timerRef.current = null;
      }, DOUBLE_TAP_DELAY);
    }
  };

  const handleAvatarPress = () => {
    router.push({
      pathname: '/media/avatar-preview',
      params: { uri: post.user.avatar, username: post.user.username.replace('@', '') }
    });
  };

  const handleUserPress = () => {
    router.push(`/user/${post.user.id}`);
  };

  return (
    <View className={`border-b border-border bg-background p-3 ${isDetail ? 'border-b-0' : ''}`}>
      <View className="flex-row items-start">
        {/* 1. Left: Avatar */}
        <TouchableOpacity onPress={handleAvatarPress}>
           <Avatar source={post.user.avatar} size="md" className="mr-3" />
        </TouchableOpacity>

        {/* 2. Right: Content Column */}
        <View className="flex-1">
          <View className="flex-row items-start justify-between">
            <TouchableOpacity onPress={handleUserPress} className="mr-2 flex-1">
              <View className="flex-row flex-wrap items-center">
                <Text className="mr-1 font-semibold text-foreground">{post.user.name}</Text>
                <Text className="text-sm text-muted-foreground" numberOfLines={1}>
                  {post.user.username}
                </Text>
              </View>
              <Text className="mt-0.5 text-xs text-muted-foreground">{post.timestamp}</Text>
            </TouchableOpacity>

            {isDetail && (
              <TouchableOpacity
                onPress={handleGoToMark}
                className="rounded-full bg-primary px-3 py-1.5"
              >
                <Text className="text-xs font-bold text-primary-foreground">Go to mark</Text>
              </TouchableOpacity>
            )}
          </View>

          {/* C. Post Content */}
          <View>
             {/* Text: Simple Press to Navigate */}
             <TouchableOpacity onPress={handlePressPost} activeOpacity={0.7}>
                <Text className="mt-2 text-base leading-5 text-foreground">{post.content}</Text>
             </TouchableOpacity>

             {/* Image: Custom Handler (Single=Preview, Double=Like) */}
             {post.images && post.images.length > 0 && (
              <Pressable onPress={handleDoubleTap} className="mt-3 relative items-center justify-center">
                <Image
                  source={{ uri: post.images[0] }}
                  className="h-48 w-full rounded-xl bg-muted"
                  resizeMode="cover"
                />
                
                {/* Heart Animation Overlay */}
                <Animated.View 
                  style={animatedHeartStyle} 
                  className="absolute pointer-events-none"
                >
                   <Icon as={Heart} size={80} color="white" fill="white" />
                </Animated.View>
              </Pressable>
            )}
          </View>

          {/* E. Action Bar */}
          <View className="mt-4 flex-row justify-between pr-4 pt-2">
            <TouchableOpacity 
              className="flex-row items-center gap-x-1"
              onPress={toggleLike}
            >
              <Icon 
                as={Heart} 
                className={isLiked ? "text-destructive" : "text-muted-foreground"} 
                fill={isLiked ? "#ef4444" : "transparent"}
                size={20} 
              />
              <Text className={isLiked ? "text-destructive font-medium text-sm" : "text-muted-foreground text-sm"}>
                {likesCount}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity 
              className="flex-row items-center gap-x-1" 
              onPress={() => !isDetail && router.push({ pathname: `/post/${post.id}`, params: { autoFocus: 'true' } })}
              disabled={isDetail}
            >
              <Icon as={MessageSquare} className="text-muted-foreground" size={20} />
              <Text className="text-sm text-muted-foreground">{post.comments}</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              className="flex-row items-center gap-x-1"
              onPress={handleShare}
            >
              <Icon as={Share2} className="text-muted-foreground" size={20} />
              <Text className="text-sm text-muted-foreground">{post.shares}</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </View>
  );
};

export { PostItem };
