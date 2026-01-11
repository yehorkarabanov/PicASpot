import React, { forwardRef } from 'react';
import { View, StyleSheet } from 'react-native';
import MapView, { PROVIDER_GOOGLE } from 'react-native-maps';
import { cn } from '@/lib/utils';
import { mapVariants } from './variants';
import type { CustomMapProps } from './types';

const defaultRegion = {
  latitude: 52.237049,
  longitude: 21.017532,
  latitudeDelta: 0.0922,
  longitudeDelta: 0.0421,
};

export const MainMap = forwardRef<MapView, CustomMapProps>(
  (
    {
      provider = PROVIDER_GOOGLE,
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
      <View
        style={{ flex: 1 }}
        className={cn(mapVariants({ variant, rounded }), className)}
      >
        <MapView
          ref={ref}
          provider={provider}
          style={[StyleSheet.absoluteFill, style]}
          initialRegion={initialRegion}
          showsUserLocation
          showsBuildings
          showsCompass
          zoomEnabled
          scrollEnabled
          rotateEnabled
          {...props}
        >
          {children}
        </MapView>
      </View>
    );
  }
);

MainMap.displayName = 'MainMap';
