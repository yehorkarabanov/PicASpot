type BadgeProgress = {
  [key: number]: number;
};

export const user = {
  name: "Alex Wanderer",
  username: "@alexwanderer",
  bio: "📸 Travel photographer, sharing the best photo spots",
  avatar:
    "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=400&h=400&fit=crop",
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
  } as BadgeProgress,
};
