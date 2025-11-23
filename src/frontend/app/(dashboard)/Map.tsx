import * as React from 'react';
import { Dimensions, View, Animated, ScrollView } from 'react-native';
import { Stack } from 'expo-router';
import { MainMap } from '@/components/map-components/main_map';
import { LIGHT_MAP, DARK_MAP } from '@/components/map-components/main_map/styles';
import { useColorScheme } from 'nativewind';
import MapView, { Marker } from 'react-native-maps';
import {markers} from '@/components/map-components/markers'
import { Text } from '@/components/ui/text';
import * as Location from 'expo-location';


export default function MapScreen() {
  const { colorScheme } = useColorScheme();
  const mapStyle = colorScheme === 'dark' ? DARK_MAP : LIGHT_MAP;
  const mapRef = React.useRef<MapView>(null);

  const {width, height} = Dimensions.get("window")
  const CARD_HEIGHT = height / 2.5;
  const CARD_WIDTH = width - 20;
  const NAV_BAR_HEIGHT = 85

  const cardAnim = React.useRef(new Animated.Value(height)).current;
  const [selectedMarker, setSelectedMarker] = React.useState<typeof markers[0] | null>(null);

  const [locationPermissionGranted, setLocationPermissionGranted] = React.useState(false);

  React.useEffect(() => {
    (async () => {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        console.log('Permission to access location was denied');
        return;
      }

      setLocationPermissionGranted(true);

      let location = await Location.getCurrentPositionAsync({});
      mapRef.current?.animateCamera(
        {
          center: {
            latitude: location.coords.latitude,
            longitude: location.coords.longitude,
          },
        },
        { duration: 500 }
      );

    })();
  }, []);

  const showCard = (markerData: typeof markers[0]) => {
    setSelectedMarker(markerData);
    Animated.timing(cardAnim, {
      toValue: height - CARD_HEIGHT - NAV_BAR_HEIGHT,
      duration: 200,
      useNativeDriver: true,
    }).start();
  };

  const hideCard = () => {
    Animated.timing(cardAnim, {
      toValue: height,
      duration: 200,
      useNativeDriver: true,
    }).start(() => {
      setSelectedMarker(null);
    });
  };

  const handleMarkerPress = (marker: typeof markers[0], index: number) => {
    showCard(marker);
  };

  return (
    <>
      <Stack.Screen options={{
        title: 'Map',
        headerShown: false,
      }}/>
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
          mapPadding={{ top: 0, right: 0, bottom: 80, left: 0 }}
          onPress={hideCard}
          customMapStyle={mapStyle}
          showsUserLocation={locationPermissionGranted}
          showsMyLocationButton={true}
        >
          {markers.map((marker, index) => (
            <Marker
              key={index}
              coordinate={marker.coordinate}
              onPress={() => handleMarkerPress(marker, index)}
            />
          ))}

        </MainMap>
        {selectedMarker && (
          <Animated.View
            style={{
              transform: [{ translateY: cardAnim }],
              width: CARD_WIDTH,
              height: CARD_HEIGHT,
              alignSelf: 'center',
            }}
            className="absolute p-4 rounded-xl bg-card shadow-2xl border border-border"
          >
            <View className="mb-2">
              <Text className="text-2xl font-bold">{selectedMarker.title}</Text>
            </View>
            <ScrollView
              className="flex-1"
              contentContainerStyle={{ paddingBottom: 20 }}
              showsVerticalScrollIndicator={false}
            >
              <Text className="text-base text-muted-foreground">
                  {selectedMarker.description}
              </Text>
            </ScrollView>
          </Animated.View>
        )}
      </View>
    </>
  );
}
