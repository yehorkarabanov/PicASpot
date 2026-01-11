import * as React from 'react';
import { useTheme } from '@/theme';
import { Dimensions, View, Animated, ScrollView, Image, ActivityIndicator, Linking, AppState } from 'react-native';
import { Stack, router } from 'expo-router';
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
import { useLandmarks } from '@/contexts/LandmarkContext';
import { cameraStyles } from '@/components/camera/cameraStyle';



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

  const [isLoadingLocation, setIsLoadingLocation] = React.useState(true);
  const cardAnim = React.useRef(new Animated.Value(height)).current;
  const [selectedMarker, setSelectedMarker] = React.useState<typeof markers[0] | null>(null);
  const [activeCircles, setActiveCircles] = React.useState<CircleData[]>([]);
  const [locationPermissionGranted, setLocationPermissionGranted] = React.useState(false);
  const [userLocation, setUserLocation] = React.useState<Coordinate | null>(null);
  const [tracksViewChanges, setTracksViewChanges] = React.useState(true);
  const [forceRedraw, setForceRedraw] = React.useState(false);
  const [showHint, setShowHint] = React.useState(false);
  const [showCamera, setShowCamera] = React.useState(false);
  const [permission, requestPermission] = useCameraPermissions();
  const [facing, setFacing] = React.useState<CameraType>('back');
  const cameraRef = React.useRef<CameraView>(null);
  const appState = React.useRef(AppState.currentState);
  const [capturedPhotoUri, setCapturedPhotoUri] = React.useState<string | null>(null);
  const { markers, fetchNearbyLandmarks } = useLandmarks();
  const [showMenu, setShowMenu] = React.useState(false);
  const menuAnim = React.useRef(new Animated.Value(0)).current;

  React.useEffect(() => {
    Animated.timing(menuAnim, {
      toValue: showMenu ? 1 : 0,
      duration: 250,
      useNativeDriver: true,
    }).start();
  }, [showMenu]);

  const getImageBaseUrl = () => {
      const apiUrl = process.env.EXPO_PUBLIC_API_URL ?? '';
      try {
        const url = new URL(apiUrl);
        url.pathname = url.pathname.replace(/\/api\/?$/, '');
        return url.toString().replace(/\/$/, '');
      } catch {
        return apiUrl.replace(/\/api\/?$/, '');
      }
    };

  const IMAGE_BASE_URL = React.useMemo(
    () => getImageBaseUrl(),
    []
  );

  React.useEffect(() => {
    setForceRedraw(true);
    const timer1 = setTimeout(() => {
      setTracksViewChanges(false);
      setForceRedraw(false);
    }, 100);
    return () => clearTimeout(timer1);
  }, [colorScheme, colors, markers]);


  React.useEffect(() => {
    let locationSubscription: Location.LocationSubscription | null = null;

    (async () => {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        console.log('Permission to access location was denied');
        setIsLoadingLocation(false);
        return;
      }

      setLocationPermissionGranted(true);

      let location = await Location.getCurrentPositionAsync({});
      setUserLocation({
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
      });

      await fetchNearbyLandmarks(location.coords.latitude, location.coords.longitude);

      /*
        Commented out for easier tests on emulator
        This would center the map camera on the user's current location
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

      // Subscribe to location updates
      locationSubscription = await Location.watchPositionAsync(
        {
          accuracy: Location.Accuracy.High,
          timeInterval: 5000,
          distanceInterval: 5,
        },
        (loc) => {
          setUserLocation({
            latitude: loc.coords.latitude,
            longitude: loc.coords.longitude,
          });
        }
      );

      setIsLoadingLocation(false);
    })();

    return () => {
      if (locationSubscription) {
        locationSubscription.remove();
      }
    };
  }, []);

  React.useEffect(() => {
    const subscription = AppState.addEventListener('change', async (nextAppState) => {
      if (
        appState.current.match(/inactive|background/) &&
        nextAppState === 'active'
      ) {
        try {
          const { status } = await Location.getForegroundPermissionsAsync();
          if (status === 'granted') {
            setLocationPermissionGranted(true);

            const location = await Location.getCurrentPositionAsync({});
            setUserLocation({
              latitude: location.coords.latitude,
              longitude: location.coords.longitude,
            });

            await fetchNearbyLandmarks(location.coords.latitude, location.coords.longitude);
          }
        } catch (error) {
          console.error('Error checking location permission on app foreground:', error);
        }
      }
      appState.current = nextAppState;
    });

    return () => {
      subscription.remove();
    };
  }, []);

  const requestPermissionAgain = async () => {
    try {
      let { status } = await Location.requestForegroundPermissionsAsync();

      if (status === 'granted') {
        setLocationPermissionGranted(true);

        const location = await Location.getCurrentPositionAsync({});
        setUserLocation({
          latitude: location.coords.latitude,
          longitude: location.coords.longitude,
        });
        await fetchNearbyLandmarks(location.coords.latitude, location.coords.longitude);

      } else if (status === 'denied') {
        Linking.openSettings();
      }
    } catch (error) {
      console.error('Error requesting location permission:', error);
      alert('An error occurred while requesting location permission.');
    }
  };


  const focusCameraOnUser = () => {
    if (!userLocation || !mapRef.current) return;

    mapRef.current.animateCamera(
      {
        center: {
          latitude: userLocation.latitude,
          longitude: userLocation.longitude,
        },
      },
      { duration: 500 }
    );
  };

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

    const normalizeImageUrl = (imageUrl: string) => {
      if (!imageUrl) return '';

      if (imageUrl.startsWith('http')) {
        return imageUrl.replace('localhost', new URL(IMAGE_BASE_URL).host);
      }
      return `${IMAGE_BASE_URL}${imageUrl}`;
    };


    const renderSimplePopup = () => {
      const hasImage = Boolean(selectedMarker?.image);
      return (
        <Modal
            visible={showHint}
            transparent={true}
            statusBarTranslucent={true}
        >
            <View className="flex-1 bg-black/90 justify-center items-center h-full w-full">

                {hasImage ? (
                    <Image
                      source={{
                        uri: normalizeImageUrl(selectedMarker?.image ?? "")
                      }}
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
                animation: "fade"
            }} />
            <View className="flex-1">
              {!locationPermissionGranted && !isLoadingLocation && (
                <View
                  className="absolute top-1/2 left-1/2 bg-background rounded-xl items-center shadow-lg border border-border"
                  style={{
                    width: 280,
                    paddingVertical: 24,
                    paddingHorizontal: 16,
                    transform: [{ translateX: -140 }, { translateY: -100 }],
                    zIndex: 10,
                  }}
                >
                  <Text className="text-lg font-bold text-center mb-4">
                    The map requires you to grant the location permissions to function properly.
                  </Text>
                  <Button variant="default" onPress={requestPermissionAgain}>
                    <Text>Open settings</Text>
                  </Button>
                </View>
              )}


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

                {locationPermissionGranted && (
                  <>
                    <View className="absolute top-12 right-4 items-end">
                      <Button
                        className="h-16 w-16 rounded-full bg-background border border-border items-center justify-center shadow-md"
                        onPress={() => setShowMenu(prev => !prev)}
                      >
                        <Ionicons name="ellipsis-vertical" size={24} color={colors.foreground} />
                      </Button>

                      {showMenu && (
                        <View className="mt-2">
                          <Button
                            className="h-16 w-16 rounded-full bg-background border border-border items-center justify-center shadow-md"
                            onPress={() => console.log('Filter button pressed')}
                            style={{ marginTop: 10 }}
                          >
                            <Ionicons name="filter-outline" size={24} color={colors.foreground} />
                          </Button>

                          <Button
                            className="h-16 w-16 rounded-full bg-background border border-border items-center justify-center shadow-md"
                            onPress={() => console.log('Reload button pressed')}
                            style={{ marginTop: 10 }}
                          >
                            <Ionicons name="reload-outline" size={24} color={colors.foreground} />
                          </Button>

                          <Button
                            className="h-16 w-16 rounded-full bg-background border border-border items-center justify-center shadow-md"
                            onPress={() => {
                              setShowMenu(false);
                              router.push('../add-marker');
                            }}

                            style={{ marginTop: 10 }}
                          >
                            <Ionicons name="add" size={24} color={colors.foreground} />
                          </Button>
                        </View>
                      )}
                    </View>

                    <View className="absolute left-4" style={{ bottom: 180 }}>
                      <Button
                        className="h-16 w-16 rounded-full bg-background border border-border items-center justify-center shadow-md"
                        onPress={() => mapRef.current?.animateCamera({ heading: 0, pitch: 0, }, { duration: 300 })}
                      >
                        <Ionicons name="compass-outline" size={24} color={colors.foreground} />
                      </Button>
                    </View>

                    <View className="absolute left-4" style={{ bottom: 110 }}>
                      <Button
                        className="h-16 w-16 rounded-full bg-background border border-border items-center justify-center shadow-md"
                        onPress={focusCameraOnUser}
                      >
                        <Ionicons name="locate-outline" size={24} color={colors.foreground} />
                      </Button>
                    </View>
                  </>
                )}

                {isLoadingLocation && (
                  <View className="absolute inset-0 bg-black/40 justify-center items-center">
                    <ActivityIndicator size="large" color={colors.primary} />
                    <Text className="mt-2 text-white font-semibold">Fetching your location...</Text>
                  </View>
                )}

                {renderAnimatedCard()}
                {renderSimplePopup()}
                {renderCameraModal()}

            </View>
        </>
    );
}

