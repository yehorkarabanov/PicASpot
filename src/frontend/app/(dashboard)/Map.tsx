import * as React from 'react';
import { useTheme } from '@/theme';
import { Dimensions, View, Animated, ScrollView, Image } from 'react-native';
import { Stack } from 'expo-router';
import { MainMap } from '@/components/map-components/main_map';
import { LIGHT_MAP, DARK_MAP } from '@/components/map-components/main_map/styles';
import { useColorScheme } from 'nativewind';
import MapView, { Marker, Callout, Circle } from 'react-native-maps';
import { markers } from '@/components/map-components/markers'
import { Text } from '@/components/ui/text';
import * as Location from 'expo-location';
import { Ionicons } from '@expo/vector-icons';
import { Button } from '@/components/ui/button';
import { Icon } from '@/components/ui/icon';
import { Modal } from 'react-native';
import { X, BadgeQuestionMark, Camera } from 'lucide-react-native';



type Coordinate = {
    latitude: number;
    longitude: number;
};

// 1. Interface definitions
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

    const { width, height } = Dimensions.get("window")
    const CARD_HEIGHT = height / 2.5;
    const CARD_WIDTH = width - 20;
    const NAV_BAR_HEIGHT = 85

    const cardAnim = React.useRef(new Animated.Value(height)).current;
    const [selectedMarker, setSelectedMarker] = React.useState<typeof markers[0] | null>(null);

    // 2. Changed state to hold an ARRAY of circles
    const [activeCircles, setActiveCircles] = React.useState<CircleData[]>([]);

    const [locationPermissionGranted, setLocationPermissionGranted] = React.useState(false);
    const [tracksViewChanges, setTracksViewChanges] = React.useState(true);
    const [forceRedraw, setForceRedraw] = React.useState(false);
    const [showHint, setShowHint] = React.useState(false);
    React.useEffect(() => {
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
        // 3. Reset array to empty
        setActiveCircles([]);
        Animated.timing(cardAnim, {
            toValue: height,
            duration: 200,
            useNativeDriver: true,
        }).start(() => {
            setSelectedMarker(null);
        });
    };

    // 4. Updated Logic to handle arrays of Custom Locations and Radii
    const handleMarkerPress = (marker: typeof markers[0], index: number) => {
        showCard(marker);

        if (marker.unlocked === 0) {
            const newCircles: CircleData[] = [];
            const hasCustomLocs = marker.customPhotoLoc && marker.customPhotoLoc.length > 0;

            if (hasCustomLocs) {
                // Iterate over the list of dicts
                marker.customPhotoLoc.forEach((loc, i) => {
                    // Get corresponding radius, or fallback to first radius, or fallback to default
                    const specificRadius = marker.radius && marker.radius[i]
                        ? marker.radius[i]
                        : (marker.radius?.[0] || DEFAULT_SEARCH_RADIUS_METERS);

                    newCircles.push({
                        center: loc,
                        radius: specificRadius
                    });
                });
            } else {
                // Fallback: One circle at marker coordinate
                newCircles.push({
                    center: marker.coordinate,
                    radius: marker.radius?.[0] || DEFAULT_SEARCH_RADIUS_METERS,
                });
            }

            setActiveCircles(newCircles);

        } else {
            setActiveCircles([]);
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
                    <View className="flex-row justify-between items-center mb-4">
                      <Text className="text-2xl text-destructive font-bold flex-1 mr-2">
                          {selectedMarker.title}
                      </Text>
                      <Button
                        className="h-12 w-12 rounded-full items-center justify-center"
                        variant="ghost"
                        size="icon"
                        onPress={() => setShowHint(true)}
                    >
                        <Icon as={BadgeQuestionMark} className="size-8 text-foreground" />
                      </Button>

                    </View>

                    {/* The rest of the content */}
                    <View className="p-4 items-center justify-center flex-1">
                        <Text className="text-lg text-muted-foreground mt-2 text-center">
                            This landmark is locked.
                        </Text>
                        <Text className="text-sm text-red-500 mt-2 font-bold">
                            Take a photo of the landmark while inside an area highlighted on map!
                        </Text>
                    </View>
                    <Button
                      className="absolute bottom-4 right-4 h-12 w-12 rounded-full items-center justify-center"
                      variant="ghost"
                      size="icon"
                      onPress={() => console.log("Launch Camera Logic Here")}
                    >
                      <Icon as={Camera} className="size-8 text-foreground" />
                    </Button>

                </AnimatedCardBase>
            );
        }
    }

    const renderSimplePopup = () => {
      const hasImage = selectedMarker?.image && selectedMarker.image !== "";
      return (
        <Modal
            visible={showHint}
            transparent={true}
            animationType="fade"
            statusBarTranslucent={true}
        >
            <View className="flex-1 bg-black/90 justify-center items-center h-full w-full">

                {hasImage ? (
                    <Image
                        source={{ uri: selectedMarker?.image || "" }}
                        style={{ width: 300, height: 300, borderRadius: 10, backgroundColor: 'white', marginBottom: 20 }}
                        resizeMode="cover"
                    />
                ) : (
                    <View
                        style={{ width: 300, height: 300, marginBottom: 20 }}
                        className="bg-card rounded-xl items-center justify-center border border-border"
                    >
                        <Ionicons name="image-outline" size={48} color="gray" />
                        <Text className="text-gray-400 mt-2 font-semibold">No photo available</Text>
                    </View>
                )}

                <Button variant="default" onPress={() => setShowHint(false)}>
                  <Icon as={X} />
                  <Text>Close</Text>
                </Button>

            </View>
        </Modal>
    );
};
    return (
        <>
            <Stack.Screen options={{
                title: 'Map',
                headerShown: false,
            }} />
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

                    {/* 5. Map over the activeCircles array */}
                    {activeCircles.map((circle, i) => (
                        <Circle
                            key={`circle-${i}`}
                            center={circle.center}
                            radius={circle.radius}
                            strokeColor={colors.primary}
                            fillColor={colors.accentTransparent}
                            strokeWidth={2}
                        />
                    ))}

                    {markers.map((marker, index) => (
                        <Marker
                            key={index}
                            coordinate={marker.coordinate}
                            pinColor={marker.unlocked === 1 ? 'green' : 'red'}
                            onPress={() => handleMarkerPress(marker, index)}
                            anchor={{ x: 0.12, y: 0.73 }}
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
                {renderSimplePopup()}

            </View>
        </>
    );
}
