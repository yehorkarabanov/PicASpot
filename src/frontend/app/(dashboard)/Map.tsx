import * as React from 'react';
import { useTheme } from '@/theme';
import { Dimensions, View, Animated, ScrollView, Image } from 'react-native';
import { Stack } from 'expo-router';
import { MainMap } from '@/components/map-components/main_map';
import { LIGHT_MAP, DARK_MAP } from '@/components/map-components/main_map/styles';
import { useColorScheme } from 'nativewind';
import MapView, { Marker, Callout, Circle } from 'react-native-maps';
import { Text } from '@/components/ui/text';
import * as Location from 'expo-location';
import { Ionicons } from '@expo/vector-icons';
import { Button } from '@/components/ui/button';
import { Icon } from '@/components/ui/icon';
import { Modal } from 'react-native';
import { X, CircleQuestionMark, Camera, Redo , RotateCw} from 'lucide-react-native';
import { CameraView, useCameraPermissions, CameraType } from 'expo-camera';
import { StyleSheet } from 'react-native';
import { useLandmarks } from '@/contexts/LandmarkContext';



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

  const { width, height } = Dimensions.get("window")
  const CARD_HEIGHT = height / 2.5;
  const CARD_WIDTH = width - 20;
  const NAV_BAR_HEIGHT = 85

  const cardAnim = React.useRef(new Animated.Value(height)).current;
  const [selectedMarker, setSelectedMarker] = React.useState<typeof markers[0] | null>(null);
  const [activeCircles, setActiveCircles] = React.useState<CircleData[]>([]);
  const [locationPermissionGranted, setLocationPermissionGranted] = React.useState(false);
  const [tracksViewChanges, setTracksViewChanges] = React.useState(true);
  const [forceRedraw, setForceRedraw] = React.useState(false);
  const [showHint, setShowHint] = React.useState(false);
  const [showCamera, setShowCamera] = React.useState(false);
  const [permission, requestPermission] = useCameraPermissions();
  const [facing, setFacing] = React.useState<CameraType>('back');
  const cameraRef = React.useRef<CameraView>(null);
  const [capturedPhotoUri, setCapturedPhotoUri] = React.useState<string | null>(null);
  const { markers, fetchNearbyLandmarks, isLoading } = useLandmarks();

  React.useEffect(() => {
    setForceRedraw(true);
    const timer1 = setTimeout(() => {
      setTracksViewChanges(false);
      setForceRedraw(false);
    }, 100);
    return () => clearTimeout(timer1);
  }, [colorScheme, colors, markers]);


    React.useEffect(() => {
        (async () => {
            let { status } = await Location.requestForegroundPermissionsAsync();
            if (status !== 'granted') {
                console.log('Permission to access location was denied');
                return;
            }

            setLocationPermissionGranted(true);
            let location = await Location.getCurrentPositionAsync({});
            await fetchNearbyLandmarks(location.coords.latitude, location.coords.longitude);
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
        setActiveCircles([]);
        Animated.timing(cardAnim, {
            toValue: height,
            duration: 200,
            useNativeDriver: true,
        }).start(() => {
            setSelectedMarker(null);
        });
    };

  const takePhoto = async () => {
      if (cameraRef.current) {
          console.log("Attempting to take photo...");
          try {
              const photo = await cameraRef.current.takePictureAsync({
                  base64: false,
                  exif: true,
              });

              console.log("Photo taken successfully! URI:", photo.uri);
              setCapturedPhotoUri(photo.uri);

          } catch (error) {
              console.error("Failed to take picture:", error);
          }
      } else {
          console.log("Camera reference is not available.");
      }
  };

  const redoPhoto = () => {
      setCapturedPhotoUri(null);
      console.log("Redo photo. Back to camera.");
  };

  const confirmPhoto = () => {
      setCapturedPhotoUri(null);
      setShowCamera(false);
      console.log("Photo confirmed and camera closed.");
  };

  const toggleCameraFacing = () => {
    setFacing(current => (current === 'back' ? 'front' : 'back'));
    console.log(`Toggling camera to: ${facing === 'back' ? 'front' : 'back'}`);
  };

  const handleMarkerPress = (marker: typeof markers[0], index: number) => {
        showCard(marker);

        if (marker.unlocked === 0) {
            const newCircles: CircleData[] = [];
            //const hasCustomLocs = marker.customPhotoLoc && marker.customPhotoLoc.length > 0;
            /*
            if (hasCustomLocs) {
                marker.customPhotoLoc.forEach((loc, i) => {
                    const specificRadius = marker.radius && marker.radius[i]
                        ? marker.radius[i]
                        : (marker.radius?.[0] || DEFAULT_SEARCH_RADIUS_METERS);

                    newCircles.push({
                        center: loc,
                        radius: specificRadius
                    });
                });
                */
           // } else {
                newCircles.push({
                    center: marker.coordinate,
                    radius: marker.radius?.[0] || DEFAULT_SEARCH_RADIUS_METERS,
                });
            //}

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
                        <Icon as={CircleQuestionMark} className="size-8 text-foreground" />
                      </Button>

                    </View>
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
                      onPress={() => setShowCamera(true)}>
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

    const renderCameraModal = () => {
        if (!permission || !permission.granted) {
            return (
                <Modal visible={showCamera} transparent={true} animationType="fade">
                    <View style={cameraStyles.permissionContainer} className="bg-background">
                        <Text className="text-lg text-foreground text-center mb-4">
                            {permission === null ? 'Loading camera permissions...' : 'We need your permission to access the camera to take a photo.'}
                        </Text>
                        {permission !== null && !permission.granted && (
                            <Button onPress={requestPermission} className="mb-4">
                                <Text>Grant Camera Permission</Text>
                            </Button>
                        )}
                        <Button variant="ghost" onPress={() => setShowCamera(false)}>
                            <Text>Close</Text>
                        </Button>
                    </View>
                </Modal>
            );
        }

return (
    <Modal
        visible={showCamera}
        transparent={false}
        animationType="slide"
        statusBarTranslucent={true}
        onRequestClose={confirmPhoto}
    >
        <View style={cameraStyles.container}>
            {capturedPhotoUri ? (
                <>
                    <Image
                        source={{ uri: capturedPhotoUri }}
                        style={cameraStyles.camera}
                        resizeMode="cover"
                    />

                    <View style={cameraStyles.previewButtonContainer}>
                        <Button
                            className="h-12 w-12 rounded-full items-center justify-center bg-black/50"
                            variant="ghost"
                            size="icon"
                            onPress={redoPhoto}
                        >
                            <Icon as={Redo} className="size-8 text-white" />
                        </Button>

                        <Button
                            className="h-12 w-12 rounded-full items-center justify-center bg-black/50"
                            variant="ghost"
                            size="icon"
                            onPress={confirmPhoto}
                        >
                            <Ionicons name="checkmark" size={30} color="white" />
                        </Button>
                    </View>
                </>
            ) : (
                <>
                    <CameraView
                        ref={cameraRef}
                        style={cameraStyles.camera}
                        facing={facing}
                    />
                    <View style={cameraStyles.closeButtonContainer}>
                      <Button
                          className="absolute top-10 right-4 h-12 w-12 rounded-full items-center justify-center bg-black/50"
                          variant="ghost"
                          size="icon"
                          onPress={confirmPhoto}
                      >
                          <Icon as={X} className="size-8 text-white" />
                      </Button>
                    </View>

                    <View style={cameraStyles.mainButtonContainer}>

                    <Button
                        className="h-12 w-12 rounded-full items-center justify-center bg-black/50"
                        variant="ghost"
                        size="icon"
                        onPress={toggleCameraFacing}
                    >
                        <Icon as={RotateCw} className="size-8 text-white" />
                    </Button>

                    <Button
                        style={cameraStyles.captureButton}
                        onPress={takePhoto}
                        size="icon"
                    >
                        <View style={cameraStyles.captureCircle} />
                    </Button>

                    <View style={{ width: 48, height: 48 }} />
                </View>
            </>
        )}
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
                            key={marker.id}
                            coordinate={marker.coordinate}
                            pinColor={marker.unlocked === 1 ? 'green' : 'red'}
                            onPress={() => handleMarkerPress(marker, index)}
                            anchor={{ x: 0.16, y: 0.98 }}
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
                {renderCameraModal()}

            </View>
        </>
    );
}


const cameraStyles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: 'black',
    },
    permissionContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20,
    },
    camera: {
        flex: 1,
        width: '100%',
    },
    closeButtonContainer: {
        position: 'absolute',
        top: 0,
        right: 0,
        zIndex: 10,
        paddingHorizontal: 16,
        paddingTop: 40,
    },

    mainButtonContainer: {
        position: 'absolute',
        bottom: 40,
        flexDirection: 'row',
        width: '100%',
        justifyContent: 'space-around',
        alignItems: 'center',
        paddingHorizontal: 16,
    },
    previewButtonContainer: {
        position: 'absolute',
        bottom: 40,
        flexDirection: 'row',
        width: '100%',
        justifyContent: 'space-between',
        paddingHorizontal: 40,
        alignItems: 'center',
    },
    captureButton: {
        width: 80,
        height: 80,
        borderRadius: 40,
        backgroundColor: 'rgba(255,255,255,0.7)',
        justifyContent: 'center',
        alignItems: 'center',
    },
    captureCircle: {
        width: 70,
        height: 70,
        borderRadius: 35,
        backgroundColor: 'white',
        borderWidth: 2,
        borderColor: 'black',
    }
});
