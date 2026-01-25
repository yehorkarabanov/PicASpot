// lib/mockData.ts

export type BadgeProgress = {
  [key: number]: number;
};

export interface UserStats {
  badges: number;
  spots: number;
  posts: number;
  followers: number;
  following: number;
  favorites: number;
}

export interface User {
  id: string;
  name: string;
  username: string;
  avatar: string;
  isFollowing: boolean;
  bio?: string;
  stats?: UserStats;
  badgeProgress?: BadgeProgress;
}

export interface Comment {
  id: string;
  username: string;
  avatar: string;
  text: string;
  likes: number;
  timestamp: string;
}

export interface Post {
  id: string;
  user: User;
  timestamp: string;
  content: string;
  images: string[];
  likes: number;
  comments: number;
  shares: number;
  latitude?: number;
  longitude?: number;
  locationName?: string;
  commentsList?: Comment[];
}

const defaultStats: UserStats = {
  badges: 5,
  spots: 12,
  posts: 8,
  followers: 120,
  following: 50,
  favorites: 30,
};

const defaultBadgeProgress: BadgeProgress = {
  1: 5,
  2: 10,
  3: 20,
};

export const mockUsers: { [key: string]: User } = {
  alex: {
    id: '1',
    name: 'Alex Wanderer',
    username: '@alexwanderer',
    avatar: 'https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=400&h=400&fit=crop',
    isFollowing: true,
    bio: '📸 Travel photographer, sharing the best photo spots',
    stats: {
      badges: 12,
      spots: 58,
      posts: 42,
      followers: 2453,
      following: 389,
      favorites: 856,
    },
    badgeProgress: {
      1: 2,
      2: 20,
      3: 15,
      4: 100,
    },
  },
  jane: {
    id: '2',
    name: 'Jane Doe',
    username: '@janedoe',
    avatar: 'https://randomuser.me/api/portraits/women/1.jpg',
    isFollowing: true,
    bio: 'Coffee lover & Code writer ☕💻',
    stats: defaultStats,
    badgeProgress: defaultBadgeProgress,
  },
  john: {
    id: '3',
    name: 'John Smith',
    username: '@johnsmith',
    avatar: 'https://randomuser.me/api/portraits/men/1.jpg',
    isFollowing: false,
    bio: 'Hiking enthusiast | Nature lover',
    stats: defaultStats,
    badgeProgress: defaultBadgeProgress,
  },
  sara: {
    id: '4',
    name: 'Sara Lee',
    username: '@saralee',
    avatar: 'https://randomuser.me/api/portraits/women/2.jpg',
    isFollowing: false,
    bio: 'Baker | Dreamer | Creator',
    stats: defaultStats,
    badgeProgress: defaultBadgeProgress,
  },
  peter: {
    id: '5',
    name: 'Peter Jones',
    username: '@peterjones',
    avatar: 'https://randomuser.me/api/portraits/men/2.jpg',
    isFollowing: true,
    bio: 'Just a guy who loves sunsets',
    stats: defaultStats,
    badgeProgress: defaultBadgeProgress,
  },
  emily: {
    id: '6',
    name: 'Emily White',
    username: '@emilywhite',
    avatar: 'https://randomuser.me/api/portraits/women/3.jpg',
    isFollowing: false,
    bio: 'Bookworm 📚',
    stats: defaultStats,
    badgeProgress: defaultBadgeProgress,
  },
};

export const MOCK_FEED_POSTS: Post[] = [
  {
    id: 'post1',
    user: mockUsers.alex,
    timestamp: '2 hours ago',
    content: 'Exploring the breathtaking views of the Swiss Alps today! 🏔️ #Travel #Switzerland',
    images: [
      'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop',
      'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&h=600&fit=crop',
      'https://images.unsplash.com/photo-1472396961693-142e6e269027?w=800&h=600&fit=crop',
    ],
    likes: 124,
    comments: 15,
    shares: 8,
    latitude: 47.3768,
    longitude: 8.5417,
    locationName: 'Zurich, Switzerland',
    commentsList: [
      {
        id: 'c1',
        username: '@jane_smith',
        avatar: 'https://randomuser.me/api/portraits/women/45.jpg',
        text: 'Wow, looks amazing! 😍',
        likes: 5,
        timestamp: '1h ago',
      },
      {
        id: 'c2',
        username: '@mark_88',
        avatar: 'https://randomuser.me/api/portraits/men/32.jpg',
        text: 'I was there last year, miss it!',
        likes: 2,
        timestamp: '30m ago',
      },
    ],
  },
  {
    id: 'post3',
    user: mockUsers.john,
    timestamp: '1 day ago',
    content:
      'Just finished a fantastic hike in the local national park. Highly recommend! 🌲 #Hiking #Nature',
    images: ['https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=800&h=600&fit=crop'],
    likes: 231,
    comments: 28,
    shares: 12,
    latitude: 51.5074,
    longitude: -0.1278,
    locationName: 'London, UK',
    commentsList: [],
  },
  {
    id: 'post5',
    user: mockUsers.alex,
    timestamp: '3 days ago',
    content: "Throwback to the serene beaches of Bali. Can't wait to go back! 🌊 #Bali #BeachLife",
    images: [
      'https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800&h=600&fit=crop',
      'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&h=600&fit=crop',
    ],
    likes: 350,
    comments: 40,
    shares: 18,
    latitude: 47.36,
    longitude: 8.5,
    locationName: 'Zurich, Switzerland',
    commentsList: [],
  },
  {
    id: 'post6',
    user: mockUsers.peter,
    timestamp: '5 hours ago',
    content: 'Another beautiful sunset from my balcony! 🌅',
    images: ['https://images.unsplash.com/photo-1511497584788-876760111969?w=800&h=600&fit=crop'],
    likes: 150,
    comments: 20,
    shares: 10,
    latitude: 51.49,
    longitude: -0.15,
    locationName: 'London, UK',
    commentsList: [],
  },
];
