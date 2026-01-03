import * as React from 'react';
import { View, ScrollView, Image, Dimensions, TouchableOpacity } from 'react-native';
import { Stack } from 'expo-router';
import { Text } from '@/components/ui/text';
import { Button } from '@/components/ui/button';
import { Icon } from '@/components/ui/icon';
import { Users, Settings, Grid, Map as MapIcon, FlagIcon, Award } from 'lucide-react-native';
import { posts } from "@/components/feed_components/posts";
import { user } from "@/components/feed_components/user";
import { useRouter } from "expo-router";

const { width } = Dimensions.get('window');
const CARD_WIDTH = (width - 32) / 3;

const badges = [
  { id: 1, label: 'Kraków, Poland', requiredSpots: 10 },
  { id: 2, label: 'Warsaw, Poland', requiredSpots: 25 },
  { id: 3, label: 'London, Great Britan', requiredSpots: 50 },
  { id: 4, label: 'Vienna, Austria', requiredSpots: 100 },
];





export default function ProfileScreen() {
  const router = useRouter();
  const [activeTab, setActiveTab] = React.useState<'posts' | 'map' | 'badges'>('posts');

  function getBadgeColor(progress: number, required: number) {
    const pct = progress / required;

    if (pct >= 0.99) return '#34cfeb';
    if (pct >= 0.6) return '#FFD700';
    if (pct >= 0.3) return '#C0C0C0';
    return '#CD7F32';
  }

  return (
    <>
      <Stack.Screen options={{
        title: 'Profile',
        headerShown: false,
        animation: 'fade',
      }} />

      <ScrollView
        className="flex-1 bg-background"
        contentContainerStyle={{ paddingBottom: 65 }}
      >
        <View className="h-40 relative">
          <View className="absolute top-10 right-4">
            <Button
              className="h-10 w-10 rounded-full items-center justify-center bg-card/90"
              variant="ghost"
              size="icon"
            >
              <Icon as={Settings} className="size-5 text-foreground" />
            </Button>
          </View>
        </View>

        <View className="px-4 -mt-16 mb-4">
          <View className="relative mb-4">
            <View className="h-32 w-32 rounded-full border-4 border-card bg-card shadow-lg overflow-hidden">
              <Image
                source={{ uri: user.avatar }}
                className="h-full w-full"
                resizeMode="cover"
              />
            </View>
          </View>

          <View className="mb-4">
            <Text className="text-3xl font-bold text-foreground mb-1">{user.name}</Text>
            <Text className="text-muted-foreground mb-3">{user.username}</Text>
            <Text className="text-foreground">{user.bio}</Text>
          </View>

        </View>

        <View className="mx-4 mb-4 p-4 rounded-2xl bg-card border border-border shadow-md">
          <View className="flex-row justify-around">
            <View className="items-center">
              <Icon as={FlagIcon} className="size-5 text-primary mb-2" />
              <Text className="text-2xl font-bold text-foreground">{user.stats.spots}</Text>
              <Text className="text-sm text-muted-foreground">Spots</Text>
            </View>
            <View className="items-center">
              <Icon as={Award} className="size-5 text-primary mb-2" />
              <Text className="text-2xl font-bold text-foreground">{user.stats.badges}</Text>
              <Text className="text-sm text-muted-foreground">Badges</Text>
            </View>
            <View className="items-center">
              <Icon as={Users} className="size-5 text-accent mb-2" />
              <Text className="text-2xl font-bold text-foreground">{user.stats.followers.toLocaleString()}</Text>
              <Text className="text-sm text-muted-foreground">Followers</Text>
            </View>

            <View className="items-center">
              <Icon as={Users} className="size-5 text-foreground mb-2" />
              <Text className="text-2xl font-bold text-foreground">{user.stats.following}</Text>
              <Text className="text-sm text-muted-foreground">Following</Text>
            </View>
          </View>
        </View>

        <View className="mx-4 mb-4 flex-row gap-2 p-2 rounded-xl bg-card border border-border shadow-md">
          <Button
            className={`flex-1 flex-row items-center justify-center gap-2 rounded-lg ${
              activeTab === 'posts' ? 'bg-primary' : 'bg-transparent'
            }`}
            variant={activeTab === 'posts' ? 'default' : 'ghost'}
            onPress={() => setActiveTab('posts')}
          >
            <Icon
              as={Grid}
              className={`size-4 ${activeTab === 'posts' ? 'text-primary-foreground' : 'text-muted-foreground'}`}
            />
            <Text className={activeTab === 'posts' ? 'text-primary-foreground font-semibold' : 'text-muted-foreground'}>
              Posts
            </Text>
          </Button>

          <Button
            className={`flex-1 flex-row items-center justify-center gap-2 rounded-lg ${
              activeTab === 'map' ? 'bg-primary' : 'bg-transparent'
            }`}
            variant={activeTab === 'map' ? 'default' : 'ghost'}
            onPress={() => setActiveTab('map')}
          >
            <Icon
              as={FlagIcon}
              className={`size-4 ${activeTab === 'map' ? 'text-primary-foreground' : 'text-muted-foreground'}`}
            />
            <Text className={activeTab === 'map' ? 'text-primary-foreground font-semibold' : 'text-muted-foreground'}>
              Spots
            </Text>
          </Button>

          <Button
            className={`flex-1 flex-row items-center justify-center gap-2 rounded-lg ${
              activeTab === 'badges' ? 'bg-primary' : 'bg-transparent'
            }`}
            variant={activeTab === 'badges' ? 'default' : 'ghost'}
            onPress={() => setActiveTab('badges')}
          >
            <Icon
              as={Award}
              className={`size-4 ${activeTab === 'badges' ? 'text-primary-foreground' : 'text-muted-foreground'}`}
            />
            <Text className={activeTab === 'badges' ? 'text-primary-foreground font-semibold' : 'text-muted-foreground'}>
              Badges
            </Text>
          </Button>

        </View>

        {activeTab === 'posts' && (
          <View className="px-4 pb-8">
            <View className="flex-row flex-wrap gap-1">
              {posts.map((post) => (
                <TouchableOpacity
                  key={post.id}
                  className="bg-card rounded-xl overflow-hidden border border-border shadow-md mb-1"
                  style={{ width: CARD_WIDTH - 4, height: CARD_WIDTH - 4 }}
                  activeOpacity={1}
                  onPress={() => router.push({ pathname: "/post/[id]", params: { id: post.id } })}
                >
                  <Image
                    source={{ uri: post.image }}
                    style={{ width: '100%', height: '100%' }}
                    resizeMode="cover"
                  />
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}

        {activeTab === 'map' && (
          <View className="mx-4 mb-8 p-8 rounded-2xl bg-card border border-border shadow-md items-center">
            <Icon as={MapIcon} className="size-16 text-primary mb-4" />
            <Text className="text-xl font-semibold text-foreground mb-2">Map View</Text>
            <Text className="text-muted-foreground text-center">
              Interactive map showing all photo locations would appear here
            </Text>
          </View>
        )}

        {activeTab === 'badges' && (
          <View className="mx-4 mb-8 p-4 rounded-2xl bg-card border border-border shadow-md">
            <Text className="text-2xl font-bold text-foreground mb-4">Badges</Text>

            <View className="gap-3">
              {badges.map((badge) => {
                const progress = user.badgeProgress[badge.id] ?? 0;
                const color = getBadgeColor(progress, badge.requiredSpots);
                const pct = Math.min(progress / badge.requiredSpots, 1);

                return (
                  <View
                    key={badge.id}
                    className="flex-row items-center gap-3 p-3 rounded-xl bg-background border border-border shadow-sm"
                  >
                    <Icon as={Award} size={48} color={color} />
                    <View className="flex-1">
                      <Text className="text-lg font-semibold text-foreground">{badge.label}</Text>
                      <Text className="text-muted-foreground text-sm">
                        {progress} / {badge.requiredSpots} spots
                      </Text>
                      <View className="h-2 w-full bg-border rounded-full mt-1">
                        <View
                          className="h-2 rounded-full"
                          style={{ width: `${pct * 100}%`, backgroundColor: color }}
                        />
                      </View>
                    </View>
                  </View>
                );
              })}
            </View>
          </View>
        )}

      </ScrollView>
    </>
  );
}
