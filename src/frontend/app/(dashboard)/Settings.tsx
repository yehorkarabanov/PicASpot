import { View } from "react-native";
import { Text } from "@/components/ui/text";
import { Stack, useRouter } from "expo-router";
import { useColorScheme } from "nativewind";
import { Button } from "@/components/ui/button";
import { Icon } from "@/components/ui/icon";
import { LogOut, MoonStarIcon, SunIcon } from "lucide-react-native";
import { useAuth } from "@/contexts/AuthContext";

const Profile = () => {
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.replace("/login");
  };

  return (
    <>
      <Stack.Screen
        options={{
          title: "Settings",
          animation: "fade",
        }}
      />
      <View className="flex-1 bg-background px-6 pt-12">
        <View className="items-end mb-8">
          <ThemeToggle />
        </View>

        <View className="bg-card shadow-lg rounded-2xl p-6 space-y-4">
          <Text className="text-card-foreground text-lg font-semibold">
            Account
          </Text>

          {user && (
            <View className="flex-row items-center justify-between">
              <Text className="text-foreground font-medium">
                {user.email}
              </Text>
              <Icon as={LogOut} className="text-destructive size-6" />
            </View>
          )}

          <Button
            variant="destructive"
            className="mt-2 rounded-xl justify-center"
            onPress={handleLogout}
          >
            <Icon as={LogOut} className="mr-2" />
            <Text className="text-primary-foreground">Logout</Text>
          </Button>
        </View>

        <View className="bg-card shadow-lg rounded-2xl p-6 mt-6 space-y-4">
          <Text className="text-card-foreground text-lg font-semibold">
            Preferences
          </Text>

          <View className="flex-row items-center justify-between">
            <Text className="text-foreground font-medium">Theme</Text>
            <ThemeToggle />
          </View>
        </View>
      </View>
    </>
  );
};

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
      className="rounded-full p-3 border border-muted shadow-sm"
    >
      <Icon as={THEME_ICONS[colorScheme ?? "light"]} className="size-5" />
    </Button>
  );
}

export default Profile;
