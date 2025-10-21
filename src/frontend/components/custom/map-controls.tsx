import { Button } from '@/components/ui/button';
import { Icon } from '@/components/ui/icon';
import { Text } from '@/components/ui/text';
import { cn } from '@/lib/utils';
import { Minus, Plus, Locate } from 'lucide-react-native';
import * as React from 'react';
import { View, ViewProps } from 'react-native';

interface MapControlsProps extends ViewProps {
  onZoomIn?: () => void;
  onZoomOut?: () => void;
  onLocate?: () => void;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
  showZoomControls?: boolean;
  showLocateControl?: boolean;
}

function MapControls({
  className,
  onZoomIn,
  onZoomOut,
  onLocate,
  position = 'top-right',
  showZoomControls = true,
  showLocateControl = true,
  ...props
}: MapControlsProps) {

  const positionClasses = {
    'top-right': 'top-3 right-3',
    'top-left': 'top-3 left-3',
    'bottom-right': 'bottom-3 right-3',
    'bottom-left': 'bottom-3 left-3',
  };

  return (
    <View
      className={cn('absolute z-10 flex-col gap-2', positionClasses[position], className)}
      {...props}
    >
      {showZoomControls && (
        <View className="overflow-hidden rounded-md border border-border/50 bg-background/95 backdrop-blur">
          <Button
            variant="ghost"
            size="icon"
            onPress={onZoomIn}
            className="h-9 w-9 rounded-none border-b border-border/50"
          >
            <Icon as={Plus} size={16} strokeWidth={2} />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onPress={onZoomOut}
            className="h-9 w-9 rounded-none"
          >
            <Icon as={Minus} size={16} strokeWidth={2} />
          </Button>
        </View>
      )}
      {showLocateControl && (
        <Button
          variant="outline"
          size="icon"
          onPress={onLocate}
          className="h-9 w-9 border-border/50 bg-background/95 backdrop-blur"
        >
          <Icon as={Locate} size={16} strokeWidth={2} />
        </Button>
      )}
    </View>
  );
}

interface MapLegendProps extends ViewProps {
  items: Array<{
    label: string;
    color?: string;
    icon?: React.ReactNode;
  }>;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
}

function MapLegend({ className, items, position = 'bottom-left', ...props }: MapLegendProps) {
  const { colorScheme } = useColorScheme();

  const positionClasses = {
    'top-right': 'top-3 right-3',
    'top-left': 'top-3 left-3',
    'bottom-right': 'bottom-3 right-3',
    'bottom-left': 'bottom-3 left-3',
  };

  return (
    <View
      className={cn(
        'absolute z-10 rounded-md border border-border/50 bg-background/95 p-3 backdrop-blur',
        positionClasses[position],
        className
      )}
      {...props}
    >
      <Text variant="small" className="mb-2 font-semibold text-foreground">
        Legend
      </Text>
      {items.map((item, index) => (
        <View key={index} className="mb-1.5 flex-row items-center gap-2 last:mb-0">
          {item.icon ? (
            item.icon
          ) : (
            <View
              className="h-2.5 w-2.5 rounded-sm"
              style={{ backgroundColor: item.color || '#000' }}
            />
          )}
          <Text variant="small" className="text-muted-foreground">
            {item.label}
          </Text>
        </View>
      ))}
    </View>
  );
}

export { MapControls, MapLegend };
export type { MapControlsProps, MapLegendProps };
export * from './map';
