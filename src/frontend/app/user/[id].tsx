import React from "react";
import { Stack, useLocalSearchParams } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { Text } from "@/components/ui/text";
import { useTheme } from "@/theme";
import { UserProfile } from "@/components/profile/UserProfile";
import { mockUsers, MOCK_FEED_POSTS } from "@/lib/mockData";

export default function UserProfileScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const colors = useTheme();

  // Find user by ID from mockUsers values or posts
  // Since mockUsers is keyed by name (alex, jane) not ID ('1', '2'), we search values
  const user = Object.values(mockUsers).find(u => u.id === id) || 
               MOCK_FEED_POSTS.find(p => p.user.id === id)?.user;

  if (!user) {
    return (
      <SafeAreaView className="flex-1 items-center justify-center bg-background">
        <Stack.Screen options={{ headerShown: true, title: "User not found" }} />
        <Text className="text-foreground">User not found</Text>
      </SafeAreaView>
    );
  }

  return (
    <>
      <Stack.Screen options={{
        title: user.username,
        headerShown: false, // UserProfile handles its own header/back button roughly
        animation: 'slide_from_right',
      }} />
      <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={['top', 'bottom']}>
        <UserProfile user={user} isCurrentUser={false} />
      </SafeAreaView>
    </>
  );
}
