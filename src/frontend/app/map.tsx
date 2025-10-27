import * as React from 'react';
import { View } from 'react-native';
import { Stack } from 'expo-router';
import { MainMap } from '@/components/map-components/main_map';
import { LIGHT_MAP, DARK_MAP } from '@/components/map-components/main_map/styles';
import { useColorScheme } from 'nativewind';
import MapView from 'react-native-maps';

export default function MapScreen() {
  const { colorScheme } = useColorScheme();
  const mapStyle = colorScheme === 'dark' ? DARK_MAP : LIGHT_MAP;
  const mapRef = React.useRef<MapView>(null);

  return (
    <>
      <Stack.Screen options={{ title: 'Map' }} />
      <View className="flex-1">
        <MainMap
          ref={mapRef}
          className="h-full w-full"
          region={{
            latitude: 50.054343,
            longitude: 19.936744,
            latitudeDelta: 0.0922,
            longitudeDelta: 0.0421,
          }}
          customMapStyle={mapStyle}
        />
      </View>
    </>
  );
}
