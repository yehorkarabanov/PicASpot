import type { MapViewProps, Region } from 'react-native-maps'
import type { VariantProps } from 'class-variance-authority'
import { mapVariants } from './variants'

export type MapVariantProps = VariantProps<typeof mapVariants>

export interface CustomMapProps extends MapViewProps {
  className?: string
  variant?: MapVariantProps['variant']
  rounded?: MapVariantProps['rounded']
  initialRegion?: Region
}
