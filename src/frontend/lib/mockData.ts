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
    bio: 'City explorer & Architecture lover 🏛️',
    stats: defaultStats,
    badgeProgress: defaultBadgeProgress,
  },
  john: {
    id: '3',
    name: 'John Smith',
    username: '@johnsmith',
    avatar: 'https://randomuser.me/api/portraits/men/1.jpg',
    isFollowing: false,
    bio: 'Hiking enthusiast | National Park chaser',
    stats: defaultStats,
    badgeProgress: defaultBadgeProgress,
  },
  sara: {
    id: '4',
    name: 'Sara Lee',
    username: '@saralee',
    avatar: 'https://randomuser.me/api/portraits/women/2.jpg',
    isFollowing: false,
    bio: 'Backpacker | Budget Traveler',
    stats: defaultStats,
    badgeProgress: defaultBadgeProgress,
  },
  peter: {
    id: '5',
    name: 'Peter Jones',
    username: '@peterjones',
    avatar: 'https://randomuser.me/api/portraits/men/2.jpg',
    isFollowing: true,
    bio: 'History buff visiting ancient ruins',
    stats: defaultStats,
    badgeProgress: defaultBadgeProgress,
  },
  emily: {
    id: '6',
    name: 'Emily White',
    username: '@emilywhite',
    avatar: 'https://randomuser.me/api/portraits/women/3.jpg',
    isFollowing: false,
    bio: 'Chasing sunsets around the world 🌍',
    stats: defaultStats,
    badgeProgress: defaultBadgeProgress,
  },
  mike: {
    id: '7',
    name: 'Mike Chen',
    username: '@mikeeats',
    avatar: 'https://randomuser.me/api/portraits/men/4.jpg',
    isFollowing: true,
    bio: 'Travel for food & culture 🍜',
    stats: defaultStats,
    badgeProgress: defaultBadgeProgress,
  },
  lisa: {
    id: '8',
    name: 'Lisa Ray',
    username: '@lisaray',
    avatar: 'https://randomuser.me/api/portraits/women/5.jpg',
    isFollowing: false,
    bio: 'Art & Museum curator on tour 🎨',
    stats: defaultStats,
    badgeProgress: defaultBadgeProgress,
  },
};

export const MOCK_FEED_POSTS: Post[] = [
  {
    id: 'post1',
    user: mockUsers.alex,
    timestamp: '2 hours ago',
    content: 'Exploring the breathtaking views of the Swiss Alps today! The air is so crisp up here.',
    images: [
      'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop',
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
    id: 'post2',
    user: mockUsers.peter,
    timestamp: '5 hours ago',
    content: 'Finally made it to the Colosseum. Standing here where history happened is absolutely surreal.',
    images: ['https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=800&h=600&fit=crop'],
    likes: 289,
    comments: 32,
    shares: 15,
    latitude: 41.8902,
    longitude: 12.4922,
    locationName: 'Rome, Italy',
    commentsList: [],
  },
  {
    id: 'post3',
    user: mockUsers.john,
    timestamp: '1 day ago',
    content:
      'The trek to Machu Picchu was challenging but this view makes every step worth it. A true wonder of the world.',
    images: ['https://images.unsplash.com/photo-1526392060635-9d6019884377?w=800&h=600&fit=crop'],
    likes: 431,
    comments: 58,
    shares: 42,
    latitude: -13.1631,
    longitude: -72.5450,
    locationName: 'Machu Picchu, Peru',
    commentsList: [],
  },
  {
    id: 'post4',
    user: mockUsers.sara,
    timestamp: '1 day ago',
    content: 'Sunrise over Angkor Wat. The reflection in the lotus pond is pure magic.',
    images: [
      'https://images.unsplash.com/photo-1600520611035-80cf9650d023?w=800&h=600&fit=crop',
    ],
    likes: 312,
    comments: 45,
    shares: 22,
    latitude: 13.4125,
    longitude: 103.8667,
    locationName: 'Siem Reap, Cambodia',
    commentsList: [],
  },
  {
    id: 'post5',
    user: mockUsers.alex,
    timestamp: '2 days ago',
    content: "Wandering through the endless red torii gates at Fushimi Inari Shrine. It feels like a portal to another world.",
    images: [
      'https://images.unsplash.com/photo-1478436127897-769e1b3f0f36?w=800&h=600&fit=crop',
    ],
    likes: 350,
    comments: 40,
    shares: 18,
    latitude: 34.9671,
    longitude: 135.7727,
    locationName: 'Kyoto, Japan',
    commentsList: [],
  },
  {
    id: 'post6',
    user: mockUsers.jane,
    timestamp: '2 days ago',
    content: 'The scale of the Grand Canyon is impossible to capture in a photo, but I had to try.',
    images: ['https://images.unsplash.com/photo-1615551043360-33de8b5f410c?w=800&h=600&fit=crop'],
    likes: 198,
    comments: 24,
    shares: 10,
    latitude: 36.1069,
    longitude: -112.1129,
    locationName: 'Arizona, USA',
    commentsList: [],
  },
  {
    id: 'post7',
    user: mockUsers.mike,
    timestamp: '3 days ago',
    content: 'Petra by night is a completely different experience. The treasury glowing by candlelight is unforgettable.',
    images: ['https://images.unsplash.com/photo-1579606728080-d667d4f07328?w=800&h=600&fit=crop'],
    likes: 210,
    comments: 34,
    shares: 15,
    latitude: 30.3285,
    longitude: 35.4444,
    locationName: 'Petra, Jordan',
    commentsList: [],
  },
  {
    id: 'post8',
    user: mockUsers.lisa,
    timestamp: '3 days ago',
    content: 'Spending the afternoon at the Louvre. The architecture of the pyramid entrance is just as impressive as the art inside.',
    images: ['https://images.unsplash.com/photo-1565099824688-e93eb20fe622?w=800&h=600&fit=crop'],
    likes: 178,
    comments: 14,
    shares: 5,
    latitude: 48.8606,
    longitude: 2.3376,
    locationName: 'Paris, France',
    commentsList: [],
  },
  {
    id: 'post9',
    user: mockUsers.john,
    timestamp: '4 days ago',
    content: 'Camping near Moraine Lake. The water is actually this blue in real life!',
    images: ['https://images.unsplash.com/photo-1536637706725-c96e883739d6?w=800&h=600&fit=crop'],
    likes: 420,
    comments: 56,
    shares: 30,
    latitude: 51.3217,
    longitude: -116.1860,
    locationName: 'Banff, Canada',
    commentsList: [],
  },
  {
    id: 'post10',
    user: mockUsers.emily,
    timestamp: '5 days ago',
    content: 'Watching the sunset over the white domes of Santorini. A dream come true.',
    images: ['https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&h=600&fit=crop'],
    likes: 295,
    comments: 42,
    shares: 20,
    latitude: 36.4618,
    longitude: 25.3753,
    locationName: 'Santorini, Greece',
    commentsList: [],
  },
  {
    id: 'post11',
    user: mockUsers.alex,
    timestamp: '5 days ago',
    content: 'Visiting the Great Wall today. It goes on forever over the hills.',
    images: ['https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800&h=600&fit=crop'],
    likes: 365,
    comments: 25,
    shares: 14,
    latitude: 40.4319,
    longitude: 116.5704,
    locationName: 'Beijing, China',
    commentsList: [],
  },
  {
    id: 'post12',
    user: mockUsers.sara,
    timestamp: '6 days ago',
    content: 'The colors of the Taj Mahal change with the light. Seeing it at sunrise was peaceful and majestic.',
    images: ['https://images.unsplash.com/photo-1564507592333-c60657eea523?w=800&h=600&fit=crop'],
    likes: 245,
    comments: 31,
    shares: 9,
    latitude: 27.1751,
    longitude: 78.0421,
    locationName: 'Agra, India',
    commentsList: [],
  },
  {
    id: 'post13',
    user: mockUsers.mike,
    timestamp: '1 week ago',
    content: 'Gazing up at the ceiling of the Sagrada Familia. Gaudi was truly a genius.',
    images: ['https://images.unsplash.com/photo-1545062428-b0a402375836?w=800&h=600&fit=crop'],
    likes: 198,
    comments: 18,
    shares: 6,
    latitude: 41.4036,
    longitude: 2.1744,
    locationName: 'Barcelona, Spain',
    commentsList: [],
  },
  {
    id: 'post14',
    user: mockUsers.jane,
    timestamp: '1 week ago',
    content: 'Walking across the Golden Gate Bridge. It gets foggy but the view of the bay is iconic.',
    images: ['https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=800&h=600&fit=crop'],
    likes: 156,
    comments: 10,
    shares: 4,
    latitude: 37.8199,
    longitude: -122.4783,
    locationName: 'San Francisco, USA',
    commentsList: [],
  },
  {
    id: 'post15',
    user: mockUsers.lisa,
    timestamp: '2 weeks ago',
    content: 'The Sydney Opera House looks like sails ready to depart. Beautiful architecture on the harbor.',
    images: ['https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=800&h=600&fit=crop'],
    likes: 412,
    comments: 65,
    shares: 28,
    latitude: -33.8568,
    longitude: 151.2153,
    locationName: 'Sydney, Australia',
    commentsList: [],
  },
];
