import * as React from 'react';
import { Button } from '@/components/ui/button';
import { Icon } from '@/components/ui/icon';
import { Text } from '@/components/ui/text';
import { useAuth } from '@/contexts/AuthContext';
import { Link, Stack, useRouter} from 'expo-router';
import { Container, LogOut, MoonStarIcon, SunIcon } from 'lucide-react-native';
import { useColorScheme } from 'nativewind';
import { View } from 'react-native';
export default function Screen() {


  return (
    <>
      <Stack.Screen options={{
        title: 'Profile',
      }}/>
      <View className="flex-1 pt-12 gap-8 p-4 bg-background">
        <View className="items-center gap-2">
          <Text className="text-foreground">
            Profile placeholder
          </Text>
        </View>
      </View>
    </>
  );
}

