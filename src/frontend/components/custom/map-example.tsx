import { Map } from '@/components/custom/map';
import { MapControls, MapLegend } from '@/components/custom/map-controls';
import { Text } from '@/components/ui/text';
import * as React from 'react';
import { View } from 'react-native';
import MapView, { Marker, Region } from 'react-native-maps';

/**
 * Example usage of the Map component with OpenStreetMap
 * This demonstrates how to use the map with controls, markers, and legends
 */
export function MapExample() {
  const mapRef = React.useRef<MapView>(null);

  const [region, setRegion] = React.useState<Region>({
    latitude: 37.78825,
    longitude: -122.4324,
    latitudeDelta: 0.0922,
    longitudeDelta: 0.0421,
  });

  const handleZoomIn = () => {
    if (mapRef.current) {
      const newRegion = {
        ...region,
        latitudeDelta: region.latitudeDelta / 2,
        longitudeDelta: region.longitudeDelta / 2,
      };
      setRegion(newRegion);
      mapRef.current.animateToRegion(newRegion, 300);
    }
  };

  const handleZoomOut = () => {
    if (mapRef.current) {
      const newRegion = {
        ...region,
        latitudeDelta: region.latitudeDelta * 2,
        longitudeDelta: region.longitudeDelta * 2,
      };
      setRegion(newRegion);
      mapRef.current.animateToRegion(newRegion, 300);
    }
  };

  const handleLocate = () => {
    // Implement user location logic here
    console.log('Locate user');
  };

  return (
    <View className="flex-1">
      <View className="h-[400px] w-full">
        <Map
          ref={mapRef}
          variant="outline"
          rounded="lg"
          className="h-full w-full"
          region={region}
          onRegionChangeComplete={setRegion}
          tileServer="osm"
        >
          {/* Example Marker */}
          <Marker
            coordinate={{
              latitude: 37.78825,
              longitude: -122.4324,
            }}
            title="Example Location"
            description="This is a sample marker"
          />
        </Map>

        {/* Map Controls */}
        <MapControls
          position="top-right"
          onZoomIn={handleZoomIn}
          onZoomOut={handleZoomOut}
          onLocate={handleLocate}
        />

        {/* Map Legend (optional) */}
        <MapLegend
          position="bottom-left"
          items={[
            { label: 'Point of Interest', color: '#ef4444' },
            { label: 'Your Location', color: '#3b82f6' },
            { label: 'Selected Area', color: '#22c55e' },
          ]}
        />
      </View>

      <View className="mt-4 p-4">
        <Text variant="h4">Map Component</Text>
        <Text variant="muted" className="mt-2">
          This map uses OpenStreetMap tiles and matches your app's shadcn design system.
        </Text>
      </View>
    </View>
  );
}
