import { cn } from '@/lib/utils';
import { cva, type VariantProps } from 'class-variance-authority';
import * as React from 'react';
import { Platform, StyleSheet, View } from 'react-native';
import MapView, { MapViewProps, UrlTile, PROVIDER_DEFAULT } from 'react-native-maps';

const mapVariants = cva('overflow-hidden', {
  variants: {
    variant: {
      default: 'bg-background',
      outline: 'border border-border/40 bg-background',
      ghost: 'bg-transparent',
    },
    rounded: {
      none: 'rounded-none',
      sm: 'rounded-sm',
      md: 'rounded-md',
      lg: 'rounded-lg',
      xl: 'rounded-xl',
    },
  },
  defaultVariants: {
    variant: 'default',
    rounded: 'lg',
  },
});

type MapVariantProps = VariantProps<typeof mapVariants>;

interface CustomMapProps extends Omit<MapViewProps, 'provider'> {
  className?: string;
  variant?: MapVariantProps['variant'];
  rounded?: MapVariantProps['rounded'];
  tileServer?: 'carto-light' | 'carto-dark' | 'carto-voyager' | 'osm' | 'custom';
  customTileUrl?: string;
  showsCompass?: boolean;
  showsScale?: boolean;
}

// Using CartoDB (CARTO) tiles - they're free, fast, and don't require API keys
const TILE_URLS = {
  'carto-light': 'https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
  'carto-dark': 'https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
  'carto-voyager': 'https://a.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png',
  osm: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
};

const Map = React.forwardRef<MapView, CustomMapProps>(
  (
    {
      className,
      variant,
      rounded,
      tileServer = 'carto-light',
      customTileUrl,
      showsCompass = false,
      showsScale = false,
      style,
      children,
      ...props
    },
    ref
  ) => {
    const tileUrl =
      tileServer === 'custom' && customTileUrl
        ? customTileUrl
        : TILE_URLS[tileServer as keyof typeof TILE_URLS] || TILE_URLS['carto-light'];

    return (
      <View className={cn(mapVariants({ variant, rounded }), className)}>
        <MapView
          ref={ref}
          provider={PROVIDER_DEFAULT}
          style={[styles.map, style]}
          showsCompass={showsCompass}
          showsScale={showsScale}
          mapType={Platform.OS === 'android' ? 'none' : 'standard'}
          showsUserLocation={false}
          showsMyLocationButton={false}
          showsPointsOfInterest={false}
          showsBuildings={true}
          showsTraffic={false}
          showsIndoors={false}
          {...props}
        >
          {Platform.OS === 'android' && (
            <UrlTile urlTemplate={tileUrl} maximumZ={19} flipY={false} zIndex={-1} />
          )}
          {children}
        </MapView>
      </View>
    );
  }
);

Map.displayName = 'Map';

const styles = StyleSheet.create({
  map: {
    width: '100%',
    height: '100%',
  },
});

export { Map, mapVariants };
export type { CustomMapProps };
