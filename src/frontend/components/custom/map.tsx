import { cn } from '@/lib/utils';
import { cva, type VariantProps } from 'class-variance-authority';
import * as React from 'react';
import { StyleSheet, View } from 'react-native';
import MapView, { MapViewProps, PROVIDER_DEFAULT, UrlTile } from 'react-native-maps';

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
  tileServer?: 'dark-nolabels';
  customTileUrl?: string;
  showsCompass?: boolean;
  showsScale?: boolean;
}

const TILE_URLS = {
  'dark-nolabels': 'https://a.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}.png',
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
    const [tilesLoaded, setTilesLoaded] = React.useState(false);

    const tileUrl =
      tileServer === 'custom' && customTileUrl
        ? customTileUrl
        : TILE_URLS[tileServer as keyof typeof TILE_URLS] || TILE_URLS['dark-nolabels'];

    React.useEffect(() => {
      setTilesLoaded(false);
      const timer = setTimeout(() => setTilesLoaded(true), 10);
      return () => clearTimeout(timer);
    }, [tileUrl]);

    return (
      <View className={cn(mapVariants({ variant, rounded }), className)}>
        <MapView
          ref={ref}
          provider={PROVIDER_DEFAULT}
          style={[styles.map, style, { opacity: tilesLoaded ? 1 : 0 }]}
          mapType="none"
          showsUserLocation={false}
          showsPointsOfInterest={false}
          showsBuildings={true}
          showsTraffic={false}
          showsIndoors={false}
          showsCompass={showsCompass}
          showsScale={showsScale}
          {...props}>
          <UrlTile
            urlTemplate={tileUrl}
            maximumZ={19}
            flipY={false}
            zIndex={10000}
          />
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
