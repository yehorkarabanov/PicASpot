import * as React from 'react';
import { View } from 'react-native';
import { Stack, useRouter } from 'expo-router';
import { Text } from '@/components/ui/text';
import { Button } from '@/components/ui/button';

export default function VerifyEmailScreen() {
  const router = useRouter();

  return (
    <View className="flex-1 justify-center px-6 py-12">
      <Stack.Screen options={{ title: 'Email Verification', headerShown: false }} />
      <View className="mb-6">
        <Text className="text-3xl font-bold mb-2">Email verification disabled</Text>
        <Text className="text-base text-muted-foreground">
          For now, email verification is disabled in this build. After registering you will receive a
          message that instructions were sent; please use the Login screen to sign in.
        </Text>
      </View>

      <View className="gap-3">
        <Button onPress={() => router.replace('/login')}
          className="mb-2">
          <Text>Go to Login</Text>
        </Button>
      </View>
    </View>
  );
}

