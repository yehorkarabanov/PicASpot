import * as React from 'react';
import { View, ScrollView, KeyboardAvoidingView, Switch, ActivityIndicator, TouchableOpacity, Image } from 'react-native';
import { Stack, router } from 'expo-router';
import { SafeAreaView, useSafeAreaInsets } from 'react-native-safe-area-context';
import { Text } from '@/components/ui/text';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { MainMap } from '@/components/map-components/main_map';
import { LIGHT_MAP, DARK_MAP } from '@/components/map-components/main_map/styles';
import { useColorScheme } from 'nativewind';
import MapView, { Marker, Region, Circle } from 'react-native-maps';
import { useTheme } from '@/theme';
import { useUserLocation } from '@/contexts/LocationContext';
import Ionicons from '@expo/vector-icons/Ionicons';
import * as ImagePicker from 'expo-image-picker';
import * as SecureStore from 'expo-secure-store';
import { useLandmarks } from '@/contexts/LandmarkContext';
import { Area, landmarkService, areaService, storageService } from '@/lib/map';
import { Alert } from 'react-native';

type Coordinate = { latitude: number; longitude: number };

export default function AddLandmarkScreen() {
  const insets = useSafeAreaInsets();
  const { colorScheme } = useColorScheme();
  const colors = useTheme();
  const mapStyle = colorScheme === 'dark' ? DARK_MAP : LIGHT_MAP;
  const { userLocation, loading } = useUserLocation();
  const { areas, fetchNearbyLandmarks } = useLandmarks();

  const [name, setName] = React.useState('');
  const [description, setDescription] = React.useState('');
  const [radius, setRadius] = React.useState('50');
  const [selectedArea, setSelectedArea] = React.useState<Area | null>(null);
  const [badgeExpanded, setBadgeExpanded] = React.useState(false);
  const [guidePhoto, setGuidePhoto] = React.useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const [landmarkLocation, setLandmarkLocation] = React.useState<Coordinate | null>(userLocation || null);
  const [photoLocation, setPhotoLocation] = React.useState<Coordinate | null>(userLocation || null);
  const [useCustomPhotoLocation, setUseCustomPhotoLocation] = React.useState(false);

  const [landmarkRegion, setLandmarkRegion] = React.useState<Region | null>(null);
  const [photoRegion, setPhotoRegion] = React.useState<Region | null>(null);

  const [tracksViewChanges, setTracksViewChanges] = React.useState(true);
  const [forceRedraw, setForceRedraw] = React.useState(false);

  const [isCreatingNewArea, setIsCreatingNewArea] = React.useState(false);
  const [newAreaName, setNewAreaName] = React.useState('');
  const [newAreaDescription, setNewAreaDescription] = React.useState('');


  const landmarkMapRef = React.useRef<MapView>(null);
  const photoMapRef = React.useRef<MapView>(null);

  React.useEffect(() => {
    setForceRedraw(true);

    const timer = setTimeout(() => {
      setTracksViewChanges(false);
      setForceRedraw(false);
    }, 100);

    return () => clearTimeout(timer);
  }, [colorScheme, colors]);

  React.useEffect(() => {
    if (userLocation) {
      setLandmarkLocation(userLocation);
      setPhotoLocation(userLocation);
      setLandmarkRegion({ ...userLocation, latitudeDelta: 0.001, longitudeDelta: 0.001 });
      setPhotoRegion({ ...userLocation, latitudeDelta: 0.001, longitudeDelta: 0.001 });

      landmarkMapRef.current?.animateToRegion({ ...userLocation, latitudeDelta: 0.005, longitudeDelta: 0.005 }, 500);
      photoMapRef.current?.animateToRegion({ ...userLocation, latitudeDelta: 0.005, longitudeDelta: 0.005 }, 500);
    }
  }, [userLocation]);

  const handleSave = async () => {
    if (!landmarkLocation) {
      Alert.alert('Error', 'Landmark location is required');
      return;
    }

    if (!name.trim()) {
      Alert.alert('Error', 'Landmark name is required');
      return;
    }

    if (!selectedArea && !isCreatingNewArea) {
      Alert.alert('Error', 'Please select an area or create a new one');
      return;
    }

    if (isCreatingNewArea && !newAreaName.trim()) {
      Alert.alert('Error', 'New area name is required');
      return;
    }

    setIsSubmitting(true);

    try {
      let areaId: string;

      if (isCreatingNewArea) {
        console.log('Creating new area:', { name: newAreaName.trim(), description: newAreaDescription.trim() });
        const newArea = await areaService.createArea({
          name: newAreaName.trim(),
          description: newAreaDescription.trim() || undefined,
        });
        console.log('New area created:', newArea);
        if (!newArea) {
          Alert.alert('Error', 'Failed to create area');
          setIsSubmitting(false);
          return;
        }
        areaId = newArea.id;
      } else if (selectedArea) {
        areaId = selectedArea.id;
      } else {
        Alert.alert('Error', 'Please select an area or create a new one');
        setIsSubmitting(false);
        return;
      }

      let imageUrl: string | undefined = undefined;
      if (guidePhoto) {
        try {
          const token = await SecureStore.getItemAsync('access_token');
          if (!token) {
            Alert.alert('Warning', 'Auth token not found, skipping photo upload');
            console.error('Auth token not found for image upload');
          } else {
            imageUrl = await storageService.uploadImage(guidePhoto, token);
            console.log('Image uploaded and ready to use:', imageUrl);
          }
        } catch (error: any) {
          Alert.alert('Warning', 'Photo upload failed, creating landmark without photo');
          console.error('Image upload failed:', error);
        }
      }

      const radiusValue = Number(radius);
      const payload: any = {
        name: name.trim(),
        description: description.trim() || undefined,
        latitude: landmarkLocation.latitude,
        longitude: landmarkLocation.longitude,
        unlock_radius_meters: radiusValue,
        photo_radius_meters: radiusValue,
        photo_location_radius: radiusValue,
        area_id: areaId,
        photo_latitude: useCustomPhotoLocation ? photoLocation?.latitude : undefined,
        photo_longitude: useCustomPhotoLocation ? photoLocation?.longitude : undefined,
      };

      // Change this part
      if (guidePhoto) {
        payload.hint_image_uri = guidePhoto;  // ← Changed from hint_image_url
      }

      console.log('Sending payload:', JSON.stringify(payload, null, 2));

      const createdLandmark = await landmarkService.createLandmark(payload);

      console.log('Full response from createLandmark:', createdLandmark);

      if (createdLandmark) {
        console.log('Landmark created successfully:', {
          id: createdLandmark.id,
          name: createdLandmark.title,
          hint_image_url: createdLandmark.hint_image_url,
        });
      } else {
        console.warn('createLandmark returned undefined or null');
      }

      if (userLocation) {
        await fetchNearbyLandmarks(userLocation.latitude, userLocation.longitude);
      }

      Alert.alert('Success', 'Landmark created successfully!', [
        { text: 'OK', onPress: () => router.back() },
      ]);
    } catch (error: any) {
      console.error('Error creating landmark:', error);
      const errorMessage =
        error.response?.data?.message ||
        error.response?.data?.detail ||
        'Failed to create landmark. Please try again.';
      Alert.alert('Error', errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };



  const pickGuidePhoto = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.7,
    });

    if (!result.canceled) {
      setGuidePhoto(result.assets[0].uri);
    }
  };

  const circleRadius = Number(radius);

  if (loading || !landmarkLocation) {
    return (
      <>
        <Stack.Screen options={{ title: '', headerTransparent: true }} />
        <View className="flex-1 justify-center items-center bg-background">
          <ActivityIndicator size="large" color={colors.primary} />
          <Text className="mt-2 text-lg text-foreground font-semibold">Fetching your location...</Text>
        </View>
      </>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-background">
      <Stack.Screen options={{ title: '', headerTransparent: true }} />
      <KeyboardAvoidingView className="flex-1" behavior="padding">
        <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={{ paddingHorizontal: 16, paddingTop: insets.top + 16, paddingBottom: 24 }}>
          <Text className="text-2xl font-bold mb-4">Add a Landmark</Text>

          <View className="bg-card rounded-lg shadow-md border border-border p-5 gap-5">

            <Field label="Name">
              <Input placeholder="Landmark name" value={name} onChangeText={setName} />
            </Field>

            <Field label="Description">
              <Input
                placeholder="Describe this landmark..."
                value={description}
                onChangeText={setDescription}
                multiline
                numberOfLines={1}
              />
            </Field>

            <Field label="Unlock Radius">
              <View className="flex-row items-center gap-3">
                <Input
                  keyboardType="numeric"
                  value={radius}
                  onChangeText={setRadius}
                  className="flex-1"
                />
                <Text className="text-muted-foreground">meters</Text>
              </View>
              <Text className="text-xs text-muted-foreground mt-1">
                Users must be within this distance to unlock the landmark
              </Text>
            </Field>

            <Field label="Area">
              <TouchableOpacity
                onPress={() => setBadgeExpanded(!badgeExpanded)}
                className="border border-border rounded-md p-3 bg-card"
              >
                <Text>
                  {isCreatingNewArea
                    ? 'Create New Area'
                    : selectedArea
                    ? selectedArea.name
                    : 'Select Area'}
                </Text>
              </TouchableOpacity>

              {badgeExpanded && (
                <View className="mt-1 border border-border rounded-md bg-card overflow-hidden">
                  {areas.length === 0 ? (
                    <View className="p-3">
                      <Text className="text-muted-foreground">No areas available nearby</Text>
                    </View>
                  ) : (
                    areas.map((area) => (
                      <TouchableOpacity
                        key={area.id}
                        onPress={() => {
                          setSelectedArea(area);
                          setIsCreatingNewArea(false);
                          setBadgeExpanded(false);
                        }}
                        className="p-3 border-b border-border"
                      >
                        <View className="flex-row items-center">
                          <View className="flex-1">
                            <Text className="font-semibold">{area.name}</Text>
                            <Text className="text-sm text-muted-foreground mt-1">
                              {area.description}
                            </Text>
                            <Text className="text-xs text-muted-foreground mt-1">
                              {area.landmark_count_in_radius} landmarks nearby
                            </Text>
                          </View>
                          {area.is_verified && (
                            <View className="items-center ml-2">
                              <Ionicons name="checkmark-circle" size={20} color={colors.primary} />
                              <Text className="text-xs text-muted-foreground mt-1">Verified</Text>
                            </View>
                          )}
                        </View>
                      </TouchableOpacity>
                    ))
                  )}

                  <TouchableOpacity
                    onPress={() => {
                      setIsCreatingNewArea(true);
                      setSelectedArea(null);
                      setBadgeExpanded(false);
                    }}
                    className="p-3 bg-primary/10"
                  >
                    <View className="flex-row items-center">
                      <Ionicons name="add-circle-outline" size={20} color={colors.primary} />
                      <Text className="ml-2 font-semibold text-primary">Create New Area</Text>
                    </View>
                  </TouchableOpacity>
                </View>
              )}

              {isCreatingNewArea && (
                <View className="mt-3 p-4 bg-primary/5 rounded-lg border border-primary/20 gap-3">
                  <View className="flex-row items-center gap-2 mb-1">
                    <Ionicons name="information-circle" size={18} color={colors.primary} />
                    <Text className="text-sm font-semibold text-primary">Creating New Area</Text>
                  </View>

                  <View>
                    <Text className="text-sm font-medium mb-2">Area Name</Text>
                    <Input
                      placeholder="e.g., Downtown District"
                      value={newAreaName}
                      onChangeText={setNewAreaName}
                    />
                  </View>

                  <View>
                    <Text className="text-sm font-medium mb-2">Area Description</Text>
                    <Input
                      placeholder="Describe this area..."
                      value={newAreaDescription}
                      onChangeText={setNewAreaDescription}
                      multiline
                      numberOfLines={3}
                      style={{
                        height: 80,
                        textAlignVertical: 'top',
                        paddingTop: 12,
                        maxHeight: 80,  // Add this
                      }}
                    />
                  </View>
                </View>
              )}
            </Field>


            <Field label="Guide Photo">
              {guidePhoto ? (
                <View className="gap-3">
                  <Image
                    source={{ uri: guidePhoto }}
                    style={{ width: '100%', height: 200, borderRadius: 12 }}
                    resizeMode="cover"
                  />
                  <View className="flex-row gap-2">
                    <Button
                      variant="outline"
                      className="flex-1"
                      onPress={pickGuidePhoto}
                    >
                      <Ionicons name="image-outline" size={18} color={colors.foreground} />
                      <Text className="ml-2">Change Photo</Text>
                    </Button>
                    <Button
                      variant="destructive"
                      className="flex-1"
                      onPress={() => setGuidePhoto(null)}
                    >
                      <Ionicons name="trash-outline" size={18} color="white" />
                      <Text className="ml-2">Remove</Text>
                    </Button>
                  </View>
                </View>
              ) : (
                <Button
                  variant="outline"
                  onPress={pickGuidePhoto}
                  className="h-32 border-2 border-dashed"
                >
                  <View className="items-center gap-2">
                    <Ionicons name="cloud-upload-outline" size={32} color={colors.muted} />
                    <Text className="text-muted-foreground">Tap to upload photo</Text>
                  </View>
                </Button>
              )}
            </Field>

            <View className="border-t border-border pt-5 mt-2">
              <View className="flex-row items-center justify-between mb-3">
                <View>
                  <Text className="text-base font-semibold">Landmark Location</Text>
                  <Text className="text-xs text-muted-foreground mt-0.5">Drag the map to position the marker</Text>
                </View>
              </View>
              <View className="h-64 rounded-lg overflow-hidden border border-border shadow-sm">
                <MainMap
                  ref={landmarkMapRef}
                  region={landmarkRegion ?? {
                    latitude: landmarkLocation.latitude,
                    longitude: landmarkLocation.longitude,
                    latitudeDelta: 0.001,
                    longitudeDelta: 0.001,
                  }}
                  showsMyLocationButton={false}
                  showsCompass={false}
                  toolbarEnabled={false}
                  customMapStyle={mapStyle}
                  onRegionChangeComplete={(region: Region) => {
                    setLandmarkLocation({ latitude: region.latitude, longitude: region.longitude });
                    setLandmarkRegion(region);
                  }}
                >
                  <Marker coordinate={landmarkLocation} anchor={{ x: 0.16, y: 0.98 }} tracksViewChanges={tracksViewChanges || forceRedraw}>
                    <Ionicons name="flag" size={30} color={colors.primary} />
                  </Marker>
                  {!useCustomPhotoLocation && (
                    <Circle center={landmarkLocation} radius={circleRadius} strokeColor={colors.primary} fillColor={colors.accentTransparent} strokeWidth={2} />
                  )}
                </MainMap>
              </View>
            </View>

            <View className="flex-row items-center justify-between mt-4 p-4 bg-muted/30 rounded-lg">
              <View className="flex-1 mr-3">
                <Text className="text-sm font-semibold mb-1">Custom Photo Location</Text>
                <Text className="text-xs text-muted-foreground">Set a different location where users must take the photo</Text>
              </View>
              <Switch
                value={useCustomPhotoLocation}
                onValueChange={(value) => {
                  setUseCustomPhotoLocation(value);
                  if (value && landmarkRegion) {
                    setPhotoLocation({ latitude: landmarkRegion.latitude, longitude: landmarkRegion.longitude });
                    setPhotoRegion(landmarkRegion);
                  }
                }}
              />
            </View>

            {useCustomPhotoLocation && photoLocation && (
              <>
                <View className="mt-4">
                  <Text className="text-base font-semibold mb-1">Photo Location</Text>
                  <Text className="text-xs text-muted-foreground mb-3">Position where the photo must be taken</Text>
                </View>
                <View className="h-64 rounded-lg overflow-hidden border border-border shadow-sm">
                  <MainMap
                    ref={photoMapRef}
                    region={photoRegion ?? {
                      latitude: photoLocation.latitude,
                      longitude: photoLocation.longitude,
                      latitudeDelta: 0.001,
                      longitudeDelta: 0.001,
                    }}
                    showsMyLocationButton={false}
                    showsCompass={false}
                    toolbarEnabled={false}
                    customMapStyle={mapStyle}
                    onRegionChangeComplete={(region: Region) => {
                      setPhotoLocation({ latitude: region.latitude, longitude: region.longitude });
                      setPhotoRegion(region);
                    }}
                  >
                    <Circle center={photoLocation} radius={circleRadius} strokeColor={colors.primary} fillColor={colors.accentTransparent} strokeWidth={2} />
                  </MainMap>
                </View>
              </>
            )}

            <View className="flex-row gap-3 mt-6 pt-4 border-t border-border">
              <Button
                variant="outline"
                className="flex-1 h-12"
                onPress={router.back}
                disabled={isSubmitting}
              >
                <Text className="font-semibold">Cancel</Text>
              </Button>
              <Button
                className="flex-1 h-12"
                onPress={handleSave}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <ActivityIndicator size="small" color="white" />
                ) : (
                  <>
                    <Ionicons name="checkmark-circle" size={20} color="white" />
                    <Text className="font-semibold ml-2">Create Landmark</Text>
                  </>
                )}
              </Button>
            </View>

          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <View className="gap-2">
      <Text className="text-sm font-medium">{label}</Text>
      {children}
    </View>
  );
}
