import React, { createContext, useContext, useState } from 'react';
import { Landmark, landmarkService, landmarkToMarker } from '@/lib/map';

interface LandmarkContextType {
  landmarks: Landmark[];
  markers: ReturnType<typeof landmarkToMarker>[];
  isLoading: boolean;
  fetchNearbyLandmarks: (latitude: number, longitude: number, radius?: number) => Promise<void>;
}

const LandmarkContext = createContext<LandmarkContextType | undefined>(undefined);

export const LandmarkProvider = ({ children }: { children: React.ReactNode }) => {
  const [landmarks, setLandmarks] = useState<Landmark[]>([]);
  const [markers, setMarkers] = useState<ReturnType<typeof landmarkToMarker>[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchNearbyLandmarks = async (latitude: number, longitude: number, radius = 1000) => {
    try {
      setIsLoading(true);
      const data = await landmarkService.getNearbyLandmarks({
        latitude,
        longitude,
        radius_meters: radius,
        only_verified: false,
        load_from_same_area: true,
        page: 1,
        page_size: 50,
      });

      setLandmarks(data);
      const mapped = data.map(landmarkToMarker);
      setMarkers(mapped);
      console.log('Fetched landmarks:', mapped); // log here
    } catch (error) {
      console.error('Failed to fetch nearby landmarks', error);
      setLandmarks([]);
      setMarkers([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <LandmarkContext.Provider value={{ landmarks, markers, isLoading, fetchNearbyLandmarks }}>
      {children}
    </LandmarkContext.Provider>
  );
};

export const useLandmarks = () => {
  const context = useContext(LandmarkContext);
  if (!context) throw new Error('useLandmarks must be used within LandmarkProvider');
  return context;
};
