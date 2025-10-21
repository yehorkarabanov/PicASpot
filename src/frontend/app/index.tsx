import * as React from 'react';
import { Button } from '@/components/ui/button';
import { Icon } from '@/components/ui/icon';
import { Text } from '@/components/ui/text';
import { useAuth } from '@/contexts/AuthContext';
import { Link, Stack, useRouter } from 'expo-router';
import { LogOut, MoonStarIcon, StarIcon, SunIcon } from 'lucide-react-native';
import { useColorScheme } from 'nativewind';
import { ActivityIndicator, Image, type ImageStyle, View } from 'react-native';

const LOGO = {
  light: require('@/assets/images/react-native-reusables-light.png'),
  dark: require('@/assets/images/react-native-reusables-dark.png'),
};

const IMAGE_STYLE: ImageStyle = {
  height: 76,
  width: 76,
};

export default function Screen() {
  const { colorScheme } = useColorScheme();
  const { user, isLoading, isAuthenticated, logout } = useAuth();
  const router = useRouter();

  React.useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace('/login');
    }
  }, [isLoading, isAuthenticated]);

  const handleLogout = async () => {
    await logout();
    router.replace('/login');
  };

  const SCREEN_OPTIONS = {
    title: 'PicASpot',
    headerTransparent: true,
    headerRight: () => <ThemeToggle />,
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

  return (
    <>
      <Stack.Screen options={SCREEN_OPTIONS} />
      <View className="flex-1 items-center justify-center gap-8 p-4">
        <Image source={LOGO[colorScheme ?? 'light']} style={IMAGE_STYLE} resizeMode="contain" />

        <View className="items-center gap-2">
          <Text className="text-2xl font-bold">Welcome to PicASpot!</Text>
          {user && (
            <Text className="text-muted-foreground">
              Logged in as: {user.email}
            </Text>
          )}
        </View>

        <View className="gap-2 p-4">
          <Text className="ios:text-foreground font-mono text-sm text-muted-foreground">
            1. Edit <Text variant="code">app/index.tsx</Text> to get started.
          </Text>
          <Text className="ios:text-foreground font-mono text-sm text-muted-foreground">
            2. Save to see your changes instantly.
          </Text>
        </View>

        <View className="flex-row gap-2">
          <Link href="https://reactnativereusables.com" asChild>
            <Button>
              <Text>Browse the Docs</Text>
            </Button>
          </Link>
          <Link href="https://github.com/founded-labs/react-native-reusables" asChild>
            <Button variant="ghost">
              <Text>Star the Repo</Text>
              <Icon as={StarIcon} />
            </Button>
          </Link>
        </View>

        <Button variant="outline" onPress={handleLogout} className="mt-4">
          <Icon as={LogOut} className="mr-2" />
          <Text>Logout</Text>
        </Button>
      </View>
    </>
  );
}

const THEME_ICONS = {
  light: SunIcon,
  dark: MoonStarIcon,
};

function ThemeToggle() {
  const { colorScheme, toggleColorScheme } = useColorScheme();

  return (
    <Button
      onPressIn={toggleColorScheme}
      size="icon"
      variant="ghost"
      className="ios:size-9 rounded-full web:mx-4">
      <Icon as={THEME_ICONS[colorScheme ?? 'light']} className="size-5" />
    </Button>
  );
}
