import * as React from 'react';
import { useTheme } from '@/theme';
import { Dimensions, View, Animated, ScrollView, Image } from 'react-native';
import { Stack } from 'expo-router';
import { MainMap } from '@/components/map-components/main_map';
import { LIGHT_MAP, DARK_MAP } from '@/components/map-components/main_map/styles';
import { useColorScheme } from 'nativewind';
import MapView, { Marker, Callout, Circle } from 'react-native-maps';
import {markers} from '@/components/map-components/markers'
import { Text } from '@/components/ui/text';
import * as Location from 'expo-location';
import { Ionicons } from '@expo/vector-icons';


type Coordinate = {
    latitude: number;
    longitude: number;
};

interface CircleData {
    center: Coordinate;
    radius: number;
}

interface AnimatedCardBaseProps {
    children: React.ReactNode;
    cardAnim: Animated.Value;
    CARD_WIDTH: number;
    CARD_HEIGHT: number;
}

const AnimatedCardBase: React.FC<AnimatedCardBaseProps> = ({ children, cardAnim, CARD_WIDTH, CARD_HEIGHT }) => (
    <Animated.View
        style={{
            transform: [{ translateY: cardAnim }],
            width: CARD_WIDTH,
            height: CARD_HEIGHT,
            alignSelf: 'center',
        }}
        className="absolute p-4 rounded-xl bg-card shadow-2xl border border-border"
    >
        {children}
    </Animated.View>
);


export default function MapScreen() {
    const { colorScheme } = useColorScheme();
    const colors = useTheme();

    const DEFAULT_SEARCH_RADIUS_METERS = 50;

    const mapStyle = colorScheme === 'dark' ? DARK_MAP : LIGHT_MAP;
    const mapRef = React.useRef<MapView>(null);

    const {width, height} = Dimensions.get("window")
    const CARD_HEIGHT = height / 2.5;
    const CARD_WIDTH = width - 20;
    const NAV_BAR_HEIGHT = 85

    const cardAnim = React.useRef(new Animated.Value(height)).current;
    const [selectedMarker, setSelectedMarker] = React.useState<typeof markers[0] | null>(null);
    const [circleData, setCircleData] = React.useState<CircleData | null>(null);
    const [locationPermissionGranted, setLocationPermissionGranted] = React.useState(false);
    const [tracksViewChanges, setTracksViewChanges] = React.useState(true);
    const [forceRedraw, setForceRedraw] = React.useState(false);

    React.useEffect(() => {
      setTracksViewChanges(true);
      setForceRedraw(true);
      const timer = setTimeout(() => {
        setTracksViewChanges(false);
        setForceRedraw(false);
      }, 100);
      return () => clearTimeout(timer);
    }, [colorScheme, colors]);

    React.useEffect(() => {
        (async () => {
            let { status } = await Location.requestForegroundPermissionsAsync();
            if (status !== 'granted') {
                console.log('Permission to access location was denied');
                return;
            }

            setLocationPermissionGranted(true);

            let location = await Location.getCurrentPositionAsync({});
            /*                                                            Commented out for easier tests on emulator
            mapRef.current?.animateCamera(
                {
                    center: {
                        latitude: location.coords.latitude,
                        longitude: location.coords.longitude,
                    },
                },
                { duration: 500 }
            );
            */

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
        setCircleData(null);
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
        const markerRadius = marker.radius || DEFAULT_SEARCH_RADIUS_METERS;
        if (marker.unlocked === 0) {
            setCircleData({
                center: marker.customPhotoLoc || marker.coordinate,
                radius: markerRadius,
            });

        } else {
            setCircleData(null);
        }
    };

    const renderAnimatedCard = () => {
        if (!selectedMarker) {
            return null;
        }
        const imageUrl = selectedMarker.image;
        const isUnlocked = selectedMarker.unlocked === 1;

        if (isUnlocked) {
            return (
                <AnimatedCardBase cardAnim={cardAnim} CARD_WIDTH={CARD_WIDTH} CARD_HEIGHT={CARD_HEIGHT}>
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
                </AnimatedCardBase>
            );
        } else {
            return (
                <AnimatedCardBase cardAnim={cardAnim} CARD_WIDTH={CARD_WIDTH} CARD_HEIGHT={CARD_HEIGHT}>
                    <View className="mb-2">
                            <Text className="text-2xl text-red-400 font-bold">{selectedMarker.title}</Text>
                    </View>
                    {imageUrl && (
                        <Image
                            source={{ uri: imageUrl }}
                            style={{ width: 100, height: 100, borderRadius: 8, marginBottom: 10 }}
                            resizeMode="cover"
                        />
                    )}
                    <View className="p-4 items-center justify-center flex-1">
                        <Text className="text-lg text-muted-foreground mt-2">
                            This landmark is locked. Photograph it to reveal its contents!
                        </Text>
                        <Text className="text-sm text-red-500 mt-2">
                            A circular search area is highlighted on the map!
                        </Text>
                    </View>
                </AnimatedCardBase>
            );
        }
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
                    showsMyLocationButton={false}
                    showsCompass={false}
                    toolbarEnabled={false}
                >
                    {circleData && (
                        <Circle
                            center={circleData.center}
                            radius={circleData.radius}
                            strokeColor={colors.primary}
                            fillColor={colors.accentTransparent}
                            strokeWidth={2}
                        />
                    )}

                    {markers.map((marker, index) => (
                        <Marker
                            key={index}
                            coordinate={marker.coordinate}
                            pinColor={marker.unlocked === 1 ? 'green' : 'red'}
                            onPress={() => handleMarkerPress(marker, index)}
                            anchor={{ x: 0.12, y: 0.73}}
                            tracksViewChanges={tracksViewChanges || forceRedraw}
                        >

                            <Ionicons
                                name={marker.unlocked === 1 ? 'flag' : 'flag-outline'}
                                size={30}
                                color={marker.unlocked === 1 ? colors.primary : colors.foreground}
                            />

                          <Callout />
                        </Marker>
                    ))}
                </MainMap>

                {renderAnimatedCard()}

            </View>
        </>
    );
}
