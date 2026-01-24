import React, { createContext, useContext, useState } from 'react';
import { Landmark, landmarkService, landmarkToMarker, Area } from '@/lib/map';

interface LandmarkContextType {
  landmarks: Landmark[];
  markers: ReturnType<typeof landmarkToMarker>[];
  areas: Area[];
  isLoading: boolean;
  fetchNearbyLandmarks: (latitude: number, longitude: number, radius?: number) => Promise<void>;
}

const LandmarkContext = createContext<LandmarkContextType | undefined>(undefined);

export const LandmarkProvider = ({ children }: { children: React.ReactNode }) => {
  const [landmarks, setLandmarks] = useState<Landmark[]>([]);
  const [markers, setMarkers] = useState<ReturnType<typeof landmarkToMarker>[]>([]);
  const [areas, setAreas] = useState<Area[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchNearbyLandmarks = async (latitude: number, longitude: number, radius = 1000) => {
    try {
      setIsLoading(true);
      const { landmarks: data, areas: fetchedAreas } = await landmarkService.getNearbyLandmarks({
        latitude,
        longitude,
        radius_meters: radius,
        only_verified: false,
        load_from_same_area: true,
        page: 1,
        page_size: 50,
      });

      setLandmarks(data);
      setAreas(fetchedAreas);

      const mapped = data.map(landmarkToMarker);
      setMarkers(mapped);

      console.log('Fetched landmarks:', data.map(l => ({
        title: l.title,
        radius: l.radius,
        unlock_radius: l.unlock_radius
      })));
      console.log('Fetched areas:', fetchedAreas.map(a => a.name));
    } catch (error) {
      console.error('Failed to fetch nearby landmarks and areas', error);
      setLandmarks([]);
      setMarkers([]);
      setAreas([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <LandmarkContext.Provider value={{ landmarks, markers, areas, isLoading, fetchNearbyLandmarks }}>
      {children}
    </LandmarkContext.Provider>
  );
};

export const useLandmarks = () => {
  const context = useContext(LandmarkContext);
  if (!context) throw new Error('useLandmarks must be used within LandmarkProvider');
  return context;
};
