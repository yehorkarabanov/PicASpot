import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity } from 'react-native';
import { Button } from '@/components/ui/button';
import { Text } from '@/components/ui/text';
import { ChevronDown } from 'lucide-react-native';
import { Icon } from '@/components/ui/icon';

interface RadiusSelectorProps {
  radius: number;
  setRadius: (radius: number) => void;
}

export const RadiusSelector: React.FC<RadiusSelectorProps> = ({ radius, setRadius }) => {
  const [isDropdownVisible, setIsDropdownVisible] = useState(false);
  const [isCustomInputVisible, setIsCustomInputVisible] = useState(false);
  const [customRadius, setCustomRadius] = useState('');

  return (
    <View className="p-4 border-b border-border z-50 bg-background">
      <TouchableOpacity 
        onPress={() => setIsDropdownVisible(!isDropdownVisible)}
        className="flex-row items-center bg-secondary px-4 py-2 rounded-full self-start border border-border"
      >
        <Text className="text-foreground font-medium mr-2">Radius: {radius} km</Text>
        <Icon as={ChevronDown} size={16} className="text-foreground" />
      </TouchableOpacity>

      {isDropdownVisible && (
        <View className="absolute top-16 left-4 bg-popover border border-border rounded-xl z-50 shadow-lg min-w-[150px]">
          <TouchableOpacity
            className="p-3 border-b border-border"
            onPress={() => {
              setRadius(1);
              setIsDropdownVisible(false);
              setIsCustomInputVisible(false);
            }}>
            <Text className="text-popover-foreground">1 km</Text>
          </TouchableOpacity>
          <TouchableOpacity
            className="p-3 border-b border-border"
            onPress={() => {
              setRadius(2);
              setIsDropdownVisible(false);
              setIsCustomInputVisible(false);
            }}>
            <Text className="text-popover-foreground">2 km</Text>
          </TouchableOpacity>
          <TouchableOpacity
            className="p-3 border-b border-border"
            onPress={() => {
              setRadius(5);
              setIsDropdownVisible(false);
              setIsCustomInputVisible(false);
            }}>
            <Text className="text-popover-foreground">5 km</Text>
          </TouchableOpacity>
          <TouchableOpacity
            className="p-3"
            onPress={() => {
              setIsCustomInputVisible(true);
              setIsDropdownVisible(false);
            }}>
            <Text className="text-popover-foreground">Custom</Text>
          </TouchableOpacity>
        </View>
      )}
      {isCustomInputVisible && (
        <View className="flex-row items-center mt-3 bg-secondary/50 p-2 rounded-lg border border-border">
          <TextInput
            placeholder="Radius (km)"
            placeholderTextColor="gray"
            className="flex-1 text-foreground text-base px-2"
            keyboardType="numeric"
            value={customRadius}
            onChangeText={setCustomRadius}
          />
          <Button
            size="sm"
            className="ml-2 h-8"
            onPress={() => {
              const newRadius = parseInt(customRadius, 10);
              if (!isNaN(newRadius)) {
                setRadius(newRadius);
              }
              setIsCustomInputVisible(false);
              setCustomRadius('');
            }}>
            <Text className="font-bold text-xs">Set</Text>
          </Button>
        </View>
      )}
    </View>
  );
};
