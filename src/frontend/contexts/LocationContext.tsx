import * as React from 'react';
import * as Location from 'expo-location';
import { AppState } from 'react-native';

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
  const appState = React.useRef(AppState.currentState);

  const fetchLocation = async () => {
    try {
      setLoading(true);

      const { status } = await Location.getForegroundPermissionsAsync();

      if (status !== 'granted') {
        setUserLocation(null);
        return;
      }

      const loc = await Location.getCurrentPositionAsync({});
      setUserLocation({
        latitude: loc.coords.latitude,
        longitude: loc.coords.longitude,
      });
    } catch (err) {
      console.error('Error fetching location:', err);
      setUserLocation(null);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchLocation();

    const sub = AppState.addEventListener('change', nextState => {
      if (
        appState.current.match(/inactive|background/) &&
        nextState === 'active'
      ) {
        fetchLocation();
      }
      appState.current = nextState;
    });

    return () => sub.remove();
  }, []);

  return (
    <LocationContext.Provider value={{ userLocation, loading }}>
      {children}
    </LocationContext.Provider>
  );
};

export const useUserLocation = () => React.useContext(LocationContext);
