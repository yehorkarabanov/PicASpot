import React from "react";
import { Stack } from "expo-router";
import { View, Text, Image, ScrollView, TouchableOpacity, FlatList } from "react-native";
import { useLocalSearchParams } from "expo-router";
import { posts } from "@/components/feed_components/posts";
import { user } from "@/components/feed_components/user";
import { SafeAreaView } from "react-native-safe-area-context";
import { useTheme } from "@/theme";
import { Feather } from '@expo/vector-icons';
import { styles as postCardStyles } from "@/components/feed_components/postCardStyle";
import { Ionicons } from "@expo/vector-icons";

export default function PostDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const post = posts.find((p) => p.id.toString() === id);
  const colors = useTheme();

  if (!post) return <Text>Post not found</Text>;

  return (
    <>
      <Stack.Screen
        options={{
          title: "",
          headerShown: true,
          headerTransparent: true,
        }}
      />

      <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
        <ScrollView contentContainerStyle={{ paddingTop: 60, paddingHorizontal: 16 }}>
          {/* Header */}
          <View style={postCardStyles.header}>
            <Image source={{ uri: user.avatar }} style={postCardStyles.avatar} />
            <View>
              <Text style={[postCardStyles.username, { color: colors.foreground }]}>{user.username}</Text>
              <Text style={[postCardStyles.location, { color: colors.mutedForeground }]}>{post.location}</Text>
            </View>
          </View>

          {/* Post content */}
          <Text style={[postCardStyles.text, { color: colors.foreground }]}>{post.text}</Text>
          <Image source={{ uri: post.image }} style={postCardStyles.image} />

          {/* Likes & Comments */}
          <View style={postCardStyles.actions}>
            <TouchableOpacity style={postCardStyles.action}>
              <Feather name="heart" size={20} color={colors.foreground} />
              <Text style={[postCardStyles.count, { color: colors.foreground }]}>{post.likes}</Text>
            </TouchableOpacity>

            <TouchableOpacity style={postCardStyles.action}>
              <Feather name="message-circle" size={20} color={colors.foreground} />
              <Text style={[postCardStyles.count, { color: colors.foreground }]}>{post.comments_nr}</Text>
            </TouchableOpacity>
          </View>

          {/* Render Comments */}
          {/* Render Comments */}
          {post.comments && post.comments.length > 0 && (
            <FlatList
              data={post.comments}
              keyExtractor={(item) => item.id.toString()}
              style={{ marginTop: 16 }}
              scrollEnabled={false} // ScrollView handles scrolling
              renderItem={({ item }) => (
                <View style={{ flexDirection: "row", marginBottom: 20, alignItems: "center" }}>
                  {/* Commenter Avatar */}
                  <Image
                    source={{ uri: item.avatar }}
                    style={{ width: 36, height: 36, borderRadius: 18, marginRight: 8 }}
                  />

                  {/* Comment Text */}
                  <View style={{ flex: 1 }}>
                    <Text style={{ fontWeight: "600", color: colors.foreground }}>
                      {item.username}
                    </Text>
                    <Text style={{ color: colors.foreground }}>{item.comment}</Text>
                  </View>

                  {/* Like Button (number left of heart) */}
                  <TouchableOpacity style={{ flexDirection: "row", alignItems: "center", gap: 4 }}>
                    {/* Swap order: number first */}
                    <Text style={{ color: colors.foreground, fontSize: 13 }}>{item.likes}</Text>
                    <Feather name="heart" size={20} color={colors.foreground} />
                  </TouchableOpacity>
                </View>
              )}
            />
          )}



        </ScrollView>
      </SafeAreaView>
    </>
  );
}
