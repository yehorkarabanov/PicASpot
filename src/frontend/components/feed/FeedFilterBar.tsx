import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity } from 'react-native';
import { Button } from '@/components/ui/button';
import { Text } from '@/components/ui/text';
import { ChevronDown } from 'lucide-react-native';
import { Icon } from '@/components/ui/icon';

export type FeedType = 'following' | 'nearby'; // Export FeedType

interface FeedFilterBarProps {
  activeFeed: FeedType;
  setActiveFeed: (feedType: FeedType) => void;
  radius: number;
  setRadius: (radius: number) => void;
}

const FeedFilterBar: React.FC<FeedFilterBarProps> = ({
  activeFeed,
  setActiveFeed,
  radius,
  setRadius,
}) => {
  const [isDropdownVisible, setIsDropdownVisible] = useState(false);
  const [isCustomInputVisible, setIsCustomInputVisible] = useState(false);
  const [customRadius, setCustomRadius] = useState('');

  return (
    <View className="border-b border-border bg-background">
      {/* Segmented Control */}
      <View className="flex-row">
        <TouchableOpacity
          onPress={() => setActiveFeed('following')}
          className={`flex-1 items-center justify-center border-b-2 p-3 ${
            activeFeed === 'following' ? 'border-primary' : 'border-transparent'
          }`}>
          <Text
            className={`font-semibold ${activeFeed === 'following' ? 'text-primary' : 'text-muted-foreground'}`}>
            Following
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          onPress={() => setActiveFeed('nearby')}
          className={`flex-1 items-center justify-center border-b-2 p-3 ${
            activeFeed === 'nearby' ? 'border-primary' : 'border-transparent'
          }`}>
          <Text
            className={`font-semibold ${activeFeed === 'nearby' ? 'text-primary' : 'text-muted-foreground'}`}>
            Nearby
          </Text>
        </TouchableOpacity>
      </View>

      {/* Radius selector */}
      {activeFeed === 'nearby' && (
        <View className="p-4 border-b border-border z-50">
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
      )}
    </View>
  );
};

export { FeedFilterBar };