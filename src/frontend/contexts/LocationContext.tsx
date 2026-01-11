import * as React from 'react';
import * as Location from 'expo-location';

export type Coordinate = { latitude: number; longitude: number };

interface LocationContextType {
  userLocation: Coordinate | null;
  loading: boolean;
}

const LocationContext = React.createContext<LocationContextType>({
  userLocation: null,
  loading: true,
});

export const LocationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [userLocation, setUserLocation] = React.useState<Coordinate | null>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    let subscription: Location.LocationSubscription | null = null;

    (async () => {
      try {
        const { status } = await Location.requestForegroundPermissionsAsync();
        if (status === 'granted') {
          const loc = await Location.getCurrentPositionAsync({});
          setUserLocation({
            latitude: loc.coords.latitude,
            longitude: loc.coords.longitude,
          });

          subscription = await Location.watchPositionAsync(
            { accuracy: Location.Accuracy.High, distanceInterval: 5 },
            (loc) => setUserLocation({ latitude: loc.coords.latitude, longitude: loc.coords.longitude })
          );
        } else {
          console.warn('Location permission denied. Using default coordinates.');
        }
      } catch (err) {
        console.error('Error fetching location:', err);
      } finally {
        setLoading(false);
      }
    })();

    return () => subscription?.remove();
  }, []);

  return (
    <LocationContext.Provider value={{ userLocation, loading }}>
      {children}
    </LocationContext.Provider>
  );
};

export const useUserLocation = () => React.useContext(LocationContext);
