import * as React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Stack, useRouter} from 'expo-router';
import { ActivityIndicator, View} from 'react-native';
import { NativeStackNavigationOptions } from '@react-navigation/native-stack';

export default function Screen() {
  const { isLoading, isAuthenticated } = useAuth();
  const router = useRouter();

  React.useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace('/login');
    }
  }, [isLoading, isAuthenticated]);

  const SCREEN_OPTIONS: NativeStackNavigationOptions = {
    title: 'PicASpot',
    headerTransparent: true,
    animation: 'slide_from_right',
  };

  if (isLoading) {
    return (
      <>
        <Stack.Screen options={SCREEN_OPTIONS} />
        <View className="flex-1 items-center justify-center">
          <ActivityIndicator size="large" />
        </View>
      </>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect to login
  }

  router.push('/Map');

  return (
    <>
    </>
  );
}


