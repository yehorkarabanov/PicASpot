import api from './api';

export interface Landmark {
  id: string;
  unlocked: boolean;
  latitude: number;
  longitude: number;
  title: string;
  description?: string;
  image?: string;
  radius: number;
  unlock_radius: number;
  badge_url?: string;
  area_id: string;
  area_name?: string;
  is_area_verified?: boolean;
}

export interface ApiResponse<T> {
  message: string;
  data: T;
}

export const landmarkService = {
  async getNearbyLandmarks(params: {
    latitude: number;
    longitude: number;
    radius_meters?: number;
    area_id?: string | null;
    only_verified?: boolean;
    load_from_same_area?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<Landmark[]> {
    const response = await api.get<ApiResponse<{ landmarks: Landmark[] }>>(
      '/v1/landmark/nearby',
      { params }
    );
    return response.data.data.landmarks;
  },
};

export function landmarkToMarker(landmark: Landmark) {
  return {
    id: landmark.id,
    unlocked: landmark.unlocked ? 1 : 0,
    coordinate: { latitude: landmark.latitude, longitude: landmark.longitude },
    title: landmark.title,
    description: landmark.description ?? '',
    image: landmark.image ?? null,
    radius: [landmark.radius],
  };
}
