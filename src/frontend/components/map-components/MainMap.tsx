import { cn } from '@/lib/utils';
import { cva, type VariantProps } from 'class-variance-authority';
import * as React from 'react';
import { StyleSheet, View } from 'react-native';
import MapView, { MapViewProps, PROVIDER_GOOGLE, Region } from 'react-native-maps';

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

interface CustomMapProps extends MapViewProps {
  className?: string;
  variant?: MapVariantProps['variant'];
  rounded?: MapVariantProps['rounded'];
}

const defaultRegion: Region = {
  latitude: 52.237049,
  longitude: 21.017532,
  latitudeDelta: 0.0922,
  longitudeDelta: 0.0421,
};

const MainMap = React.forwardRef<MapView, CustomMapProps>(
  (
    {
      provider = PROVIDER_GOOGLE,
      //googleMapId = '1607aff22cefbda1205b59d7',
      className,
      variant,
      rounded,
      style,
      initialRegion = defaultRegion,
      children,
      ...props
    },
    ref
  ) => {

    return (
      <View className={cn(mapVariants({ variant, rounded }), className)}>
        <MapView
          ref={ref}
          provider={provider}
          //googleMapId={googleMapId}
          style={styles.map}
          initialRegion={initialRegion}
          showsUserLocation={true}
          showsBuildings={true}
          showsCompass={true}
          zoomEnabled={true}
          scrollEnabled={true}
          rotateEnabled={true}
          {...props}>
          {children}
        </MapView>
      </View>
    );
  }
);

MainMap.displayName = 'Map';

const styles = StyleSheet.create({
  map: {
    flex: 1
  },
});

export { MainMap, mapVariants };
export type { CustomMapProps };
