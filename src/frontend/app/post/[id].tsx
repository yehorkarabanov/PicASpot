import React from "react";
import { Stack, useLocalSearchParams } from "expo-router";
import { View, ScrollView, TouchableOpacity, Image } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useTheme } from "@/theme";
import { MOCK_FEED_POSTS } from "@/lib/mockData";
import { Text } from "@/components/ui/text";
import { PostItem } from "@/components/feed/PostItem";
import { Feather } from '@expo/vector-icons';

export default function PostDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  
  // Simulate database fetch using the universal ID
  // Handle generated IDs from the feed (e.g., "post1-0") by stripping the suffix
  const post = MOCK_FEED_POSTS.find((p) => p.id === id) || 
               MOCK_FEED_POSTS.find((p) => id?.startsWith(p.id));
  
  const colors = useTheme();

  if (!post) {
    return (
      <SafeAreaView className="flex-1 items-center justify-center bg-background">
        <Text className="text-foreground">Post not found</Text>
      </SafeAreaView>
    );
  }

  return (
    <>
      <Stack.Screen
        options={{
          headerTitle: "Post",
          headerShown: true,
          headerBackTitle: "Back",
          headerStyle: { backgroundColor: colors.background },
          headerTintColor: colors.foreground,
          animation: 'slide_from_right',
        }}
      />

      <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={['bottom', 'left', 'right']}>
        <ScrollView contentContainerStyle={{ paddingBottom: 20 }}>
          {/* Reuse the exact PostItem component */}
          <PostItem post={post} isDetail={true} />

          {/* Divider */}
          <View className="h-[1px] w-full bg-border" />

          {/* Comments Section */}
          <View className="px-4 pt-4">
            <Text className="mb-4 text-lg font-bold text-foreground">Comments</Text>
            
            {post.commentsList && post.commentsList.length > 0 ? (
               post.commentsList.map((item) => (
                <View key={item.id} className="mb-5 flex-row items-start">
                  {/* Commenter Avatar */}
                  <Image
                    source={{ uri: item.avatar }}
                    className="mr-3 h-9 w-9 rounded-full bg-muted"
                  />

                  {/* Comment Content */}
                  <View className="flex-1">
                    <View className="mb-0.5 flex-row items-center">
                        <Text className="mr-2 font-semibold text-foreground">
                          {item.username}
                        </Text>
                        <Text className="text-xs text-muted-foreground">
                            {item.timestamp}
                        </Text>
                    </View>
                    <Text className="leading-5 text-foreground">{item.text}</Text>
                  </View>

                  {/* Comment Like Button */}
                  <TouchableOpacity className="ml-2 items-center">
                     <Feather name="heart" size={14} color={colors.mutedForeground} />
                     <Text className="mt-0.5 text-[10px] text-muted-foreground">{item.likes}</Text>
                  </TouchableOpacity>
                </View>
              ))
            ) : (
                <View className="py-4">
                  <Text className="text-center text-muted-foreground">No comments yet. Be the first to say something!</Text>
                </View>
            )}
          </View>
        </ScrollView>
      </SafeAreaView>
    </>
  );
}
