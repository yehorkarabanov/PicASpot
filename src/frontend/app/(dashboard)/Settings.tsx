import { View } from "react-native"
import { Text } from "@/components/ui/text";
import { Stack, useRouter } from 'expo-router';
import { useColorScheme } from 'nativewind';
import { Button } from '@/components/ui/button';
import { Icon } from '@/components/ui/icon';
import { LogOut, MoonStarIcon, SunIcon } from 'lucide-react-native';
import { useAuth } from '@/contexts/AuthContext';

const Profile = () => {
   const { user, logout } = useAuth();
    const router = useRouter();

    const handleLogout = async () => {
      await logout();
      router.replace('/login');
    };


  return (
    <>
      <Stack.Screen options={{
        title: 'Settings',
      }}/>
      <View className="flex-1 pt-12 gap-8 p-4 bg-background">
        <ThemeToggle />
        <View className="items-center gap-2">
          {user && (
            <Text className="text-foreground">
              Logged in as: {user.email}
            </Text>
          )}
          <Button variant="default" onPress={handleLogout}>
            <Icon as={LogOut} className="mr-2" />
            <Text>Logout</Text>
          </Button>
          </View>
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

export default Profile;
