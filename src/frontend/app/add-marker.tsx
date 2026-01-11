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

type Coordinate = { latitude: number; longitude: number };

export default function AddLandmarkScreen() {
  const insets = useSafeAreaInsets();
  const { colorScheme } = useColorScheme();
  const colors = useTheme();
  const mapStyle = colorScheme === 'dark' ? DARK_MAP : LIGHT_MAP;
  const { userLocation, loading } = useUserLocation();

  const [name, setName] = React.useState('');
  const [description, setDescription] = React.useState('');
  const [radius, setRadius] = React.useState('50');
  const [badge, setBadge] = React.useState<string | null>(null);
  const [badgeExpanded, setBadgeExpanded] = React.useState(false);
  const [guidePhoto, setGuidePhoto] = React.useState<string | null>(null);

  const [landmarkLocation, setLandmarkLocation] = React.useState<Coordinate | null>(userLocation || null);
  const [photoLocation, setPhotoLocation] = React.useState<Coordinate | null>(userLocation || null);
  const [useCustomPhotoLocation, setUseCustomPhotoLocation] = React.useState(false);

  const [landmarkRegion, setLandmarkRegion] = React.useState<Region | null>(null);
  const [photoRegion, setPhotoRegion] = React.useState<Region | null>(null);

  const [tracksViewChanges, setTracksViewChanges] = React.useState(true);
  const [forceRedraw, setForceRedraw] = React.useState(false);



  const landmarkMapRef = React.useRef<MapView>(null);
  const photoMapRef = React.useRef<MapView>(null);

  const badges = ['Krakow, Old Town', 'Krakow, Kazimierz', 'Krakow, Nowa Huta', 'Adventurer'];

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

  const handleSave = () => {
    if (!landmarkLocation) return;

    const payload = {
      name,
      description,
      latitude: landmarkLocation.latitude,
      longitude: landmarkLocation.longitude,
      unlock_radius_meters: Number(radius),
      badge,
      guidePhoto,
      photo_latitude: useCustomPhotoLocation ? photoLocation?.latitude : undefined,
      photo_longitude: useCustomPhotoLocation ? photoLocation?.longitude : undefined,
    };

    console.log('Landmark payload:', payload);
    setTimeout(() => router.back(), 50);

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
      <View className="flex-1 justify-center items-center bg-background">
        <ActivityIndicator size="large" color={colors.primary} />
        <Text className="mt-2 text-lg text-foreground font-semibold">Fetching your location...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-background">
      <Stack.Screen options={{ title: '', headerTransparent: true }} />
      <KeyboardAvoidingView className="flex-1" behavior="padding">
        <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={{ paddingHorizontal: 16, paddingTop: insets.top + 16, paddingBottom: 24 }}>
          <Text className="text-2xl font-bold mb-4">Add a Landmark</Text>

          <View className="bg-card rounded-md shadow-md border border-border p-4 gap-4">

            <Field label="Name">
              <Input placeholder="Landmark name" value={name} onChangeText={setName} />
            </Field>

            <Field label="Description">
              <Input placeholder="Short description" value={description} onChangeText={setDescription} />
            </Field>

            <Field label="Radius (meters)">
              <Input keyboardType="numeric" value={radius} onChangeText={setRadius} />
            </Field>

            <Field label="Badge">
              <TouchableOpacity onPress={() => setBadgeExpanded(!badgeExpanded)} className="border border-border rounded-md p-3 bg-card">
                <Text>{badge ?? 'Select Badge'}</Text>
              </TouchableOpacity>
              {badgeExpanded && (
                <View className="mt-1 border border-border rounded-md bg-card overflow-hidden">
                  {badges.map((b) => (
                    <TouchableOpacity key={b} onPress={() => { setBadge(b); setBadgeExpanded(false); }} className="p-3 border-b border-border last:border-b-0">
                      <Text>{b}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
              )}
            </Field>

            <Field label="Guide Photo">
              <Button variant="outline" onPress={pickGuidePhoto}>
                <Text>{guidePhoto ? 'Change Photo' : 'Upload Photo'}</Text>
              </Button>
              {guidePhoto && <Image source={{ uri: guidePhoto }} style={{ width: 100, height: 100, marginTop: 8, borderRadius: 8 }} />}
            </Field>

            <Text className="text-sm font-medium mb-2">Landmark Location</Text>
            <View className="h-64 rounded-md overflow-hidden border border-border">
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
                <Marker coordinate={landmarkLocation} anchor={{ x: 0.16, y: 0.98 }}  tracksViewChanges={tracksViewChanges || forceRedraw}>
                  <Ionicons name="flag" size={30} color={colors.primary} />
                </Marker>
                {!useCustomPhotoLocation && (
                  <Circle center={landmarkLocation} radius={circleRadius} strokeColor={colors.primary} fillColor={colors.accentTransparent} strokeWidth={2} />
                )}
              </MainMap>
            </View>

            <View className="flex-row items-center justify-between mt-4">
              <Text className="text-sm font-medium">Custom photo location?</Text>
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
                <Text className="text-sm font-medium mt-2">Photo Location</Text>
                <View className="h-64 rounded-md overflow-hidden border border-border">
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

            <View className="flex-row gap-3 mt-4">
              <Button variant="outline" className="flex-1 border border-border" onPress={router.back}>
                <Text>Cancel</Text>
              </Button>
              <Button className="flex-1" onPress={handleSave}>
                <Text>Submit</Text>
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
