import * as React from 'react';
import { useTheme } from '@/theme';
import { View, ScrollView, Image, Dimensions, TouchableOpacity } from 'react-native';
import { Stack } from 'expo-router';
import { useColorScheme } from 'nativewind';
import { Text } from '@/components/ui/text';
import { Button } from '@/components/ui/button';
import { Icon } from '@/components/ui/icon';
import { Users, Settings, Grid, Map as MapIcon, FlagIcon, Award } from 'lucide-react-native';

const { width } = Dimensions.get('window');
const CARD_WIDTH = (width - 32) / 3;

type BadgeProgress = {
  [key: number]: number;
};

const user = {
  name: "Alex Wanderer",
  username: "@alexwanderer",
  bio: "📸 Travel photographer, sharing the best photo spots",
  avatar: "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=400&h=400&fit=crop",
  stats: {
    badges: 12,
    spots: 58,
    posts: 42,
    followers: 2453,
    following: 389,
    favorites: 856
  },
    badgeProgress:{
    1: 2,
    2: 20,
    3: 15,
    4: 100,
  } as BadgeProgress,
}
const posts = [
  { id: 1, image: "https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=400&h=400&fit=crop", likes: 234, comments: 45, location: "Paris, France" },
  { id: 2, image: "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=400&h=400&fit=crop", likes: 189, comments: 32, location: "Amsterdam" },
  { id: 3, image: "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=400&h=400&fit=crop", likes: 312, comments: 67, location: "Tokyo, Japan" },
  { id: 4, image: "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=400&h=400&fit=crop", likes: 445, comments: 89, location: "Santorini, Greece" },
  { id: 5, image: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=400&fit=crop", likes: 278, comments: 54, location: "Swiss Alps" },
  { id: 6, image: "https://images.unsplash.com/photo-1493246507139-91e8fad9978e?w=400&h=400&fit=crop", likes: 201, comments: 38, location: "Iceland" },

  { id: 7, image: "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=400&h=400&fit=crop", likes: 356, comments: 72, location: "New York, USA" },
  { id: 8, image: "https://images.unsplash.com/photo-1494475673543-6a6a27143b22?w=400&h=400&fit=crop", likes: 412, comments: 81, location: "Rome, Italy" },
  { id: 9, image: "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=400&h=400&fit=crop", likes: 299, comments: 50, location: "Bali, Indonesia" },
  { id: 10, image: "https://images.unsplash.com/photo-1501785888041-cb9f3e29e9c4?w=400&h=400&fit=crop", likes: 187, comments: 29, location: "Kyoto, Japan" },
  { id: 11, image: "https://images.unsplash.com/photo-1483683804023-6ccdb62f86ef?w=400&h=400&fit=crop", likes: 402, comments: 90, location: "London, UK" },
  { id: 12, image: "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=400&h=400&fit=crop", likes: 265, comments: 47, location: "Sydney, Australia" },

  { id: 13, image: "https://images.unsplash.com/photo-1495567720989-cebdbdd97913?w=400&h=400&fit=crop", likes: 331, comments: 66, location: "Los Angeles, USA" },
  { id: 14, image: "https://images.unsplash.com/photo-1494526585095-c41746248156?w=400&h=400&fit=crop", likes: 215, comments: 43, location: "Barcelona, Spain" },
  { id: 15, image: "https://images.unsplash.com/photo-1451186859696-371d9477be93?w=400&h=400&fit=crop", likes: 452, comments: 93, location: "Norway Fjords" },
  { id: 16, image: "https://images.unsplash.com/photo-1470770903676-69b98201ea1c?w=400&h=400&fit=crop", likes: 182, comments: 24, location: "Toronto, Canada" },
  { id: 17, image: "https://images.unsplash.com/photo-1458442310124-dde6edb43d10?w=400&h=400&fit=crop", likes: 388, comments: 78, location: "Venice, Italy" },
  { id: 18, image: "https://images.unsplash.com/photo-1457264635001-828d0cbd483e?w=400&h=400&fit=crop", likes: 231, comments: 31, location: "Lisbon, Portugal" },

  { id: 19, image: "https://images.unsplash.com/photo-1482192596544-9eb780fc7f66?w=400&h=400&fit=crop", likes: 344, comments: 56, location: "Berlin, Germany" },
  { id: 20, image: "https://images.unsplash.com/photo-1472214103451-9374bd1c798e?w=400&h=400&fit=crop", likes: 199, comments: 33, location: "Dubai, UAE" },
  { id: 21, image: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=400&h=400&fit=crop", likes: 416, comments: 74, location: "Cape Town, South Africa" },
  { id: 22, image: "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=400&fit=crop", likes: 187, comments: 26, location: "Marrakech, Morocco" },
  { id: 23, image: "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=400&h=400&fit=crop", likes: 328, comments: 67, location: "Phuket, Thailand" },
  { id: 24, image: "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=400&h=400&fit=crop", likes: 253, comments: 39, location: "Hanoi, Vietnam" },

  { id: 25, image: "https://images.unsplash.com/photo-1456327102063-fb5054efe647?w=400&h=400&fit=crop", likes: 299, comments: 57, location: "Moscow, Russia" },
  { id: 26, image: "https://images.unsplash.com/photo-1437652010333-fbf2cd02a4f8?w=400&h=400&fit=crop", likes: 211, comments: 20, location: "Athens, Greece" },
  { id: 27, image: "https://images.unsplash.com/photo-1519677100203-a0e668c92439?w=400&h=400&fit=crop", likes: 478, comments: 112, location: "Rio de Janeiro, Brazil" },
  { id: 28, image: "https://images.unsplash.com/photo-1513595086754-ad0b7da6ce49?w=400&h=400&fit=crop", likes: 188, comments: 25, location: "Helsinki, Finland" },
  { id: 29, image: "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=400&h=400&fit=crop", likes: 363, comments: 69, location: "Seoul, South Korea" },
  { id: 30, image: "https://images.unsplash.com/photo-1491553895911-0055eca6402d?w=400&h=400&fit=crop", likes: 278, comments: 46, location: "San Francisco, USA" },

  { id: 31, image: "https://images.unsplash.com/photo-1506084868230-bb9d95c24759?w=400&h=400&fit=crop", likes: 342, comments: 58, location: "Stockholm, Sweden" },
  { id: 32, image: "https://images.unsplash.com/photo-1500048993953-d23a436266cf?w=400&h=400&fit=crop", likes: 227, comments: 41, location: "Budapest, Hungary" },
  { id: 33, image: "https://images.unsplash.com/photo-1494526585095-c41746248156?w=400&h=400&fit=crop", likes: 399, comments: 91, location: "Prague, Czech Republic" },
  { id: 34, image: "https://images.unsplash.com/photo-1470770841072-f978cf4d019e?w=400&h=400&fit=crop", likes: 311, comments: 63, location: "Copenhagen, Denmark" },
  { id: 35, image: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=400&h=400&fit=crop", likes: 256, comments: 35, location: "Johannesburg, South Africa" },
  { id: 36, image: "https://images.unsplash.com/photo-1433878455169-469f13f7e91a?w=400&h=400&fit=crop", likes: 421, comments: 84, location: "Maldives" },

  { id: 37, image: "https://images.unsplash.com/photo-1473621038790-a38a5cbf3088?w=400&h=400&fit=crop", likes: 367, comments: 59, location: "Hong Kong" },
  { id: 38, image: "https://images.unsplash.com/photo-1491349174775-aaafddd81942?w=400&h=400&fit=crop", likes: 191, comments: 28, location: "Zurich, Switzerland" },
  { id: 39, image: "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=400&h=400&fit=crop", likes: 402, comments: 88, location: "Singapore" },
  { id: 40, image: "https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?w=400&h=400&fit=crop", likes: 268, comments: 36, location: "Auckland, New Zealand" },
  { id: 41, image: "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=400&h=400&fit=crop", likes: 312, comments: 43, location: "Melbourne, Australia" },
  { id: 42, image: "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=400&h=400&fit=crop", likes: 277, comments: 41, location: "Hawaii, USA" },

  { id: 43, image: "https://images.unsplash.com/photo-1483683804023-6ccdb62f86ef?w=400&h=400&fit=crop", likes: 341, comments: 57, location: "Manchester, UK" },
  { id: 44, image: "https://images.unsplash.com/photo-1457264635001-828d0cbd483e?w=400&h=400&fit=crop", likes: 298, comments: 49, location: "Nice, France" },
  { id: 45, image: "https://images.unsplash.com/photo-1457264635001-b1b8cb5c5c43?w=400&h=400&fit=crop", likes: 263, comments: 38, location: "Naples, Italy" },
  { id: 46, image: "https://images.unsplash.com/photo-1472214103451-9374bd1c798e?w=400&h=400&fit=crop", likes: 186, comments: 22, location: "Doha, Qatar" },
  { id: 47, image: "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=400&fit=crop", likes: 442, comments: 97, location: "Casablanca, Morocco" },
  { id: 48, image: "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=400&h=400&fit=crop", likes: 354, comments: 77, location: "Chiang Mai, Thailand" },

  { id: 49, image: "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=400&h=400&fit=crop", likes: 219, comments: 39, location: "Seville, Spain" },
  { id: 50, image: "https://images.unsplash.com/photo-1457264635001-828d0cbd483e?w=400&h=400&fit=crop", likes: 367, comments: 58, location: "Vienna, Austria" }
];

const badges = [
  { id: 1, label: 'Kraków, Poland', requiredSpots: 10 },
  { id: 2, label: 'Warsaw, Poland', requiredSpots: 25 },
  { id: 3, label: 'London, Great Britan', requiredSpots: 50 },
  { id: 4, label: 'Vienna, Austria', requiredSpots: 100 },
];





export default function ProfileScreen() {
  const { colorScheme } = useColorScheme();
  const colors = useTheme();
  const [activeTab, setActiveTab] = React.useState<'posts' | 'map' | 'badges'>('posts');

  function getBadgeColor(progress: number, required: number) {
    const pct = progress / required;

    if (pct >= 0.99) return '#34cfeb';
    if (pct >= 0.6) return '#FFD700';
    if (pct >= 0.3) return '#C0C0C0';
    return '#CD7F32';
  }


  function getBadgeProgress(userSpots: number, badge: { requiredSpots: number }) {
    return Math.min(userSpots / badge.requiredSpots, 1); // 0-1
  }


  return (
    <>
      <Stack.Screen options={{
        title: 'Profile',
        headerShown: false,
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

          <Button className="mb-4 rounded-full">
            <Text className="font-semibold">Follow</Text>
          </Button>
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

        {/* Tabs */}
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
