import { Button } from '@/components/ui/button';
import { Icon } from '@/components/ui/icon';
import { Map } from '@/components/custom/map';
import { MapControls, MapLegend } from '@/components/custom/map-controls';
import { Stack } from 'expo-router';
import { MoonStarIcon, SunIcon } from 'lucide-react-native';
import { useColorScheme } from 'nativewind';
import * as React from 'react';
import { type ImageStyle, View } from 'react-native';
import MapView, { Marker, Region } from 'react-native-maps';

const LOGO = {
  light: require('@/assets/images/react-native-reusables-light.png'),
  dark: require('@/assets/images/react-native-reusables-dark.png'),
};

const SCREEN_OPTIONS = {
  title: 'React Native Reusables',
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

  const [region, setRegion] = React.useState<Region>({
    latitude: 50.054343,
    longitude: 19.936744,
    latitudeDelta: 0.0922,
    longitudeDelta: 0.0421,
  });

  const handleZoomIn = () => {
    if (mapRef.current) {
      const newRegion = {
        ...region,
        latitudeDelta: region.latitudeDelta / 2,
        longitudeDelta: region.longitudeDelta / 2,
      };
      setRegion(newRegion);
      mapRef.current.animateToRegion(newRegion, 300);
    }
  };

  const handleZoomOut = () => {
    if (mapRef.current) {
      const newRegion = {
        ...region,
        latitudeDelta: region.latitudeDelta * 2,
        longitudeDelta: region.longitudeDelta * 2,
      };
      setRegion(newRegion);
      mapRef.current.animateToRegion(newRegion, 300);
    }
  };

  const handleLocate = () => {
    // TODO: Implement user location logic
    console.log('Locate user');
  };

  return (
    <>
      <Stack.Screen options={SCREEN_OPTIONS} />
      <View className="flex-1 bg-background p-4">
        <View className="h-full w-full">
          <Map
            ref={mapRef}
            variant="outline"
            rounded="lg"
            className="h-full w-full"
            region={region}
            onRegionChangeComplete={setRegion}
            tileServer={colorScheme === 'dark' ? 'carto-dark' : 'carto-light'}
          >
            <Marker
              coordinate={{
                latitude: 50.054343,
                longitude: 19.936744,
              }}
              title="Example Location"
              description="This is a sample marker"
            />
          </Map>

          <MapControls
            position="top-right"
            onZoomIn={handleZoomIn}
            onZoomOut={handleZoomOut}
            onLocate={handleLocate}
          />

          {/*<MapLegend*/}
          {/*  position="bottom-left"*/}
          {/*  items={[*/}
          {/*    { label: 'Haha', color: '#ef4444' },*/}
          {/*  ]}*/}
          {/*/>*/}
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
