import api from './api';

export interface Landmark {
  id: string;
  unlocked: boolean;
  latitude: number;
  longitude: number;
  title: string;
  description?: string;
  image?: string;
  hint_image_url?: string;
  radius: number;
  unlock_radius: number;
  badge_url?: string;
  area_id: string;
  area_name?: string;
  is_area_verified?: boolean;
}

export interface Area {
  id: string;
  name: string;
  description: string;
  is_verified: boolean;
  image_url: string;
  badge_url: string;
  created_at: string;
  updated_at: string;
  landmark_count_in_radius: number;
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
  }): Promise<{ landmarks: Landmark[]; areas: Area[] }> {
    const [landmarksResponse, areasResponse] = await Promise.all([
      api.get<ApiResponse<{ landmarks: Landmark[] }>>(
        '/v1/landmark/nearby',
        { params }
      ),
      api.get<ApiResponse<{
        areas: Area[];
        total: number;
        page: number;
        page_size: number;
        total_pages: number;
        count: number;
      }>>(
        '/v1/area/nearby',
        {
          params: {
            latitude: params.latitude,
            longitude: params.longitude,
            radius_meters: params.radius_meters || 50000,
            only_verified: true,
            page_size: 50,
          }
        }
      ),
    ]);

    return {
      landmarks: landmarksResponse.data.data.landmarks,
      areas: areasResponse.data.data.areas,
    };
  },

  async createLandmark(params: {
    name: string;
    description?: string;
    latitude: number;
    longitude: number;
    unlock_radius_meters: number;
    area_id: string;
    photo_latitude?: number;
    photo_longitude?: number;
    hint_image_url?: string;
  }): Promise<Landmark> {
    console.log('Creating landmark with params:', params);

    try {
      const params_obj: any = {
        name: params.name,
        latitude: params.latitude,
        longitude: params.longitude,
        unlock_radius_meters: params.unlock_radius_meters,
        photo_radius_meters: 50,
        area_id: params.area_id,
        hint_image_url: ""
      };

      if (params.description) {
        params_obj.description = params.description;
      }
      if (params.photo_latitude !== undefined && params.photo_longitude !== undefined) {
        params_obj.photo_latitude = params.photo_latitude;
        params_obj.photo_longitude = params.photo_longitude;
        params_obj.photo_location_radius = 50;
      }
      if (params.hint_image_url) {
        params_obj.hint_image_url = params.hint_image_url;
      }

      console.log('Sending as query parameters:', params_obj);

      const response = await api.post<ApiResponse<{ landmark: Landmark }>>(
        '/v1/landmark/',
        null,
        {
          params: params_obj,
          timeout: 30000,
          maxRedirects: 5,
        }
      );

      console.log('Landmark created successfully:', response.data);
      return response.data.data.landmark;
    } catch (error: any) {
      console.error('Full error object:', error);
      if (error.message) console.error('Error message:', error.message);
      if (error.code) console.error('Error code:', error.code);
      if (error.response?.status) console.error('Response status:', error.response.status);
      if (error.response?.data) console.error('Response data:', error.response.data);
      throw error;
    }
  },
};

export const areaService = {
  async getNearbyAreas(params: {
    latitude: number;
    longitude: number;
    radius_meters?: number;
    only_verified?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<Area[]> {
    const response = await api.get<ApiResponse<{
      areas: Area[];
      total: number;
      page: number;
      page_size: number;
      total_pages: number;
      count: number;
    }>>(
      '/v1/area/nearby',
      { params }
    );
    return response.data.data.areas;
  },

  async createArea(params: {
    name: string;
    description?: string;
  }): Promise<Area> {
    const queryParams: any = {
      name: params.name,
    };
    if (params.description) {
      queryParams.description = params.description;
    }

    try {
      const response = await api.post<any>(
        '/v1/area/',
        null,
        {
          params: queryParams,
          timeout: 30000,
          maxRedirects: 5,
        }
      );

      console.log('Area creation response:', response.data);

      const area = response.data.data?.area || response.data.data || response.data;
      return area;
    } catch (error: any) {
      console.error('Error creating area:', error.response?.data || error.message);
      throw error;
    }
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
    hint_image_url: landmark.hint_image_url ?? null,
    radius: [landmark.unlock_radius || landmark.radius],
  };
}

export const storageService = {
  async uploadImage(imageUri: string, token: string): Promise<string> {
    const formData = new FormData();

    const filename = imageUri.split('/').pop() || 'landmark-image.jpg';
    formData.append('file', {
      uri: imageUri,
      type: 'image/jpeg',
      name: filename,
    } as any);

    try {
      console.log('Uploading image:', filename);
      const apiUrl = process.env.EXPO_PUBLIC_API_URL || 'https://192.168.1.108/api';

      const response = await fetch(`${apiUrl}/v1/storage/upload?folder=landmark_guides`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(JSON.stringify(error));
      }

      const data = await response.json();
      console.log('Full upload response:', JSON.stringify(data, null, 2));

      const publicUrl = data.data?.public_url || data.public_url || data.url;
      if (!publicUrl) {
        console.error('No public_url found in response. Response structure:', data);
        throw new Error(`Unexpected response structure: ${JSON.stringify(data)}`);
      }

      console.log('Image uploaded successfully:', publicUrl);
      return publicUrl;
    } catch (error: any) {
      console.error('Error uploading image:', error.message);
      throw error;
    }
  },
};

// Function to calculate distance between two points using Haversine formula
export function getDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371; // Radius of Earth in kilometers
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c; // Distance in km
  return distance;
}