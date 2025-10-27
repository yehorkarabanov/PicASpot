import { Button } from '@/components/ui/button';
import { Icon } from '@/components/ui/icon';
import { Text } from '@/components/ui/text';
import { MainMap } from '@/components/map-components/main_map'
import { DARK_MAP, LIGHT_MAP } from '@/components/map-components/main_map/styles'
import MapView, { Region } from 'react-native-maps';
import { Link, Stack } from 'expo-router';
import { Container, MoonStarIcon, StarIcon, SunIcon } from 'lucide-react-native';
import { useColorScheme } from 'nativewind';
import * as React from 'react';
import { Image, type ImageStyle, View } from 'react-native';

const LOGO = {
  light: require('@/assets/images/react-native-reusables-light.png'),
  dark: require('@/assets/images/react-native-reusables-dark.png'),
};

const SCREEN_OPTIONS = {
  title: '',
  headerTransparent: true,
  headerRight: () => <ThemeToggle />,
};

const IMAGE_STYLE: ImageStyle = {
  height: 76,
  width: 76,
};

export default function Screen() {
  const { colorScheme } = useColorScheme();
  const mapRef = React.useRef<MapView>(null);
  const [region] = React.useState<Region>({
    latitude: 50.054343,
    longitude: 19.936744,
    latitudeDelta: 0.0922,
    longitudeDelta: 0.0421,
  });

  const mapKey = colorScheme ?? 'light';
  const mapStyle = colorScheme === 'dark' ? DARK_MAP : LIGHT_MAP;


  return (
    <>
      <Stack.Screen options={SCREEN_OPTIONS} />
      <View className="flex-1">
        <MainMap
          key={mapKey}
          ref={mapRef}
          className="h-full w-full"
          region={region}
          customMapStyle={mapStyle}
          >
        </MainMap>
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

