import React from "react";
import { FlatList } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Stack } from "expo-router";
import { useTheme } from '@/theme';
import { PostCard } from "@/components/feed_components/PostCard";
import { posts } from "@/components/feed_components/posts";
import { user } from "@/components/feed_components/user";

export default function Feed() {
  const colors = useTheme();

  return (
    <>
      <Stack.Screen
        options={{
          title: "Feed",
          animation: 'fade',
        }}
      />

      <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={["top"]} >
        <FlatList
          data={posts}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <PostCard
              postId={item.id}
              username={user.username}
              avatar={user.avatar}
              text={item.text}
              image={item.image}
              location={item.location}
              likes={item.likes}
              comments_nr={item.comments_nr}
              comments={item.comments}
            />
          )}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={{
            paddingBottom: 80,
          }}
        />
      </SafeAreaView>
    </>
  );
}
