import * as React from 'react';
import { Stack } from 'expo-router';
import { UserProfile } from '@/components/profile/UserProfile';
import { MOCK_FEED_POSTS } from '@/lib/mockData';

// Assuming Alex is the logged-in user for this prototype
const CURRENT_USER_ID = '1'; 

export default function ProfileScreen() {
  const currentUser = MOCK_FEED_POSTS.find(p => p.user.id === CURRENT_USER_ID)?.user || MOCK_FEED_POSTS[0].user;

  return (
    <>
      <Stack.Screen options={{
        title: 'Profile',
        headerShown: false,
        animation: 'fade',
      }} />
      <UserProfile user={currentUser} isCurrentUser={true} />
    </>
  );
}