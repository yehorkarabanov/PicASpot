import React from 'react';
import { View, TouchableOpacity } from 'react-native';
import { Text } from '@/components/ui/text';

export type FeedType = 'following' | 'nearby';

interface FeedFilterBarProps {
  activeFeed: FeedType;
  setActiveFeed: (feedType: FeedType) => void;
}

const FeedFilterBar: React.FC<FeedFilterBarProps> = ({ activeFeed, setActiveFeed }) => {
  return (
    <View className="bg-background">
      {}
      <View className="flex-row border-b border-border">
        <TouchableOpacity
          onPress={() => setActiveFeed('following')}
          className={`flex-1 items-center justify-center border-b-2 p-3 ${
            activeFeed === 'following' ? 'border-foreground' : 'border-transparent'
          }`}>
          <Text
            className={`font-semibold ${activeFeed === 'following' ? 'text-foreground' : 'text-muted-foreground'}`}>
            Following
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          onPress={() => setActiveFeed('nearby')}
          className={`flex-1 items-center justify-center border-b-2 p-3 ${
            activeFeed === 'nearby' ? 'border-foreground' : 'border-transparent'
          }`}>
          <Text
            className={`font-semibold ${activeFeed === 'nearby' ? 'text-foreground' : 'text-muted-foreground'}`}>
            Nearby
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

export { FeedFilterBar };
