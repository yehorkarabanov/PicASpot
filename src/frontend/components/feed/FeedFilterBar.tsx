import React, { useState } from 'react';
import { View, TouchableOpacity, TextInput } from 'react-native';
import { Text } from '@/components/ui/text';
import { Button } from '@/components/ui/button';

export type FeedType = 'following' | 'nearby';

interface FeedFilterBarProps {
  activeFeed: FeedType;
  setActiveFeed: (feedType: FeedType) => void;
  radius: number;
  setRadius: (radius: number) => void;
}

export const FeedFilterBar: React.FC<FeedFilterBarProps> = ({
  activeFeed,
  setActiveFeed,
  radius,
  setRadius,
}) => {
  const [isDropdownVisible, setIsDropdownVisible] = useState(false);
  const [isCustomInputVisible, setIsCustomInputVisible] = useState(false);
  const [customRadius, setCustomRadius] = useState('');

  return (
    <View className="bg-card border-b border-border z-10">
      {/* 1. The Tabs */}
      <View className="flex-row">
        <TouchableOpacity
          onPress={() => setActiveFeed('following')}
          className={`flex-1 items-center justify-center border-b-2 p-3 ${
            activeFeed === 'following' ? 'border-primary' : 'border-transparent'
          }`}>
          <Text className={`font-semibold ${activeFeed === 'following' ? 'text-primary' : 'text-muted-foreground'}`}>
            Following
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          onPress={() => setActiveFeed('nearby')}
          className={`flex-1 items-center justify-center border-b-2 p-3 ${
            activeFeed === 'nearby' ? 'border-primary' : 'border-transparent'
          }`}>
          <Text className={`font-semibold ${activeFeed === 'nearby' ? 'text-primary' : 'text-muted-foreground'}`}>
            Nearby
          </Text>
        </TouchableOpacity>
      </View>

      {/* 2. The Radius Filter (Only shows for Nearby) */}
      {activeFeed === 'nearby' && (
        <View className="p-3 bg-muted/20">
             {/* ... (Keep your existing Radius/Dropdown logic here) ... */}
             <TouchableOpacity onPress={() => setIsDropdownVisible(!isDropdownVisible)}>
                <Text className="text-foreground text-sm">📍 Radius: <Text className="font-bold">{radius} km</Text></Text>
             </TouchableOpacity>
             
             {/* Dropped the full dropdown code for brevity, insert your existing logic here */}
        </View>
      )}
    </View>
  );
};
