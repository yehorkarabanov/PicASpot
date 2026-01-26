import React, { useState, useRef, useEffect } from 'react';
import { Stack, useLocalSearchParams } from 'expo-router';
import {
  View,
  ScrollView,
  TouchableOpacity,
  Image,
  TextInput,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '@/theme';
import { MOCK_FEED_POSTS } from '@/lib/mockData';
import { Text } from '@/components/ui/text';
import { PostItem } from '@/components/feed/PostItem';
import { Feather } from '@expo/vector-icons';
import { Avatar } from '@/components/ui/Avatar';
import { useAuth } from '@/contexts/AuthContext';
import { Icon } from '@/components/ui/icon';
import { Send } from 'lucide-react-native';
import { cn } from '@/lib/utils';

export default function PostDetail() {
  const { id, autoFocus } = useLocalSearchParams<{ id: string; autoFocus?: string }>();
  const { user } = useAuth();
  const inputRef = useRef<TextInput>(null);
  const [isFocused, setIsFocused] = useState(false);

  const post =
    MOCK_FEED_POSTS.find((p) => p.id === id) || MOCK_FEED_POSTS.find((p) => id?.startsWith(p.id));

  const colors = useTheme();

  const [comments, setComments] = useState(post?.commentsList || []);
  const [newComment, setNewComment] = useState('');

  useEffect(() => {
    if (autoFocus === 'true' && inputRef.current) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 500);
    }
  }, [autoFocus]);

  if (!post) {
    return (
      <SafeAreaView className="flex-1 items-center justify-center bg-background">
        <Text className="text-foreground">Post not found</Text>
      </SafeAreaView>
    );
  }

  const handleSendComment = () => {
    if (!newComment.trim()) return;

    const newCommentObj = {
      id: `comment-${Date.now()}`,
      username: user?.username || 'You',
      avatar: user?.avatar_url || 'https://github.com/shadcn.png',
      text: newComment.trim(),
      timestamp: 'Just now',
      likes: 0,
    };

    setComments([newCommentObj, ...comments]);
    setNewComment('');
    inputRef.current?.blur();
  };

  return (
    <SafeAreaView
      style={{ flex: 1, backgroundColor: colors.background }}
      edges={['bottom', 'left', 'right']}>
      <Stack.Screen
        options={{
          headerTitle: 'Post',
          headerShown: true,
          headerBackTitle: 'Back',
          headerStyle: { backgroundColor: colors.background },
          headerTintColor: colors.foreground,
          animation: 'slide_from_right',
        }}
      />

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{ flex: 1 }}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 100 : 0}>
        <ScrollView contentContainerStyle={{ paddingBottom: 20 }}>
          {}
          <PostItem post={post} isDetail={true} />

          {}
          <View className="h-[1px] w-full bg-border" />

          {}
          <View className="px-4 pt-4">
            <Text className="mb-4 text-lg font-bold text-foreground">Comments</Text>

            {}
            <View className="mb-6 flex-row items-center gap-3">
              <Avatar source={user?.avatar_url || 'https://github.com/shadcn.png'} size="sm" />
              <View
                className={cn(
                  'flex-1 flex-row items-center rounded-full border bg-secondary/30 px-4 py-2',
                  isFocused ? 'border-primary bg-secondary/50' : 'border-border'
                )}>
                <TextInput
                  ref={inputRef}
                  placeholder="Add a comment..."
                  placeholderTextColor={colors.mutedForeground}
                  className="mr-2 min-h-[24px] flex-1 text-foreground"
                  multiline
                  value={newComment}
                  onChangeText={setNewComment}
                  onFocus={() => setIsFocused(true)}
                  onBlur={() => setIsFocused(false)}
                />
                <TouchableOpacity
                  onPress={handleSendComment}
                  disabled={!newComment.trim()}
                  className={!newComment.trim() ? 'opacity-50' : 'opacity-100'}>
                  <Icon
                    as={Send}
                    size={20}
                    className={isFocused ? 'text-primary' : 'text-muted-foreground'}
                  />
                </TouchableOpacity>
              </View>
            </View>

            {comments.length > 0 ? (
              comments.map((item) => (
                <View key={item.id} className="mb-5 flex-row items-start">
                  {}
                  <Image
                    source={{ uri: item.avatar }}
                    className="mr-3 h-9 w-9 rounded-full bg-muted"
                  />

                  {}
                  <View className="flex-1">
                    <View className="mb-0.5 flex-row items-center">
                      <Text className="mr-2 font-semibold text-foreground">{item.username}</Text>
                      <Text className="text-xs text-muted-foreground">{item.timestamp}</Text>
                    </View>
                    <Text className="leading-5 text-foreground">{item.text}</Text>
                  </View>

                  {}
                  <TouchableOpacity className="ml-2 items-center">
                    <Feather name="heart" size={14} color={colors.mutedForeground} />
                    <Text className="mt-0.5 text-[10px] text-muted-foreground">{item.likes}</Text>
                  </TouchableOpacity>
                </View>
              ))
            ) : (
              <View className="py-4">
                <Text className="text-center text-muted-foreground">
                  No comments yet. Be the first to say something!
                </Text>
              </View>
            )}
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
