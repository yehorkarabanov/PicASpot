import { useState, useEffect, useMemo } from 'react';
import { Post, MOCK_FEED_POSTS } from '@/lib/mockData';
import { getDistance } from '@/lib/map';

type FeedType = 'following' | 'nearby';

interface UsePostsOptions {
  type: FeedType;
  radius?: number; // in km
  userLocation?: { latitude: number; longitude: number };
}

export const usePosts = ({ type, radius, userLocation }: UsePostsOptions) => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);

    const timer = setTimeout(() => {
      if (!isMounted) return;

      try {
        let filteredPosts: Post[] = [];

        if (type === 'following') {
          filteredPosts = MOCK_FEED_POSTS.filter((post) => post.user.isFollowing);
        } else if (type === 'nearby') {
          if (userLocation && radius) {
            filteredPosts = MOCK_FEED_POSTS.filter((post) => {
              if (!post.latitude || !post.longitude) return false;
              const distance = getDistance(
                userLocation.latitude,
                userLocation.longitude,
                post.latitude,
                post.longitude
              );
              return distance <= radius;
            });
          } else {
            filteredPosts = MOCK_FEED_POSTS;
          }
        }

        const augmentedPosts = Array.from({ length: 5 }).flatMap((_, i) =>
          filteredPosts.map((post) => ({
            ...post,
            id: `${post.id}-${type}-${i}`,
          }))
        );

        setPosts(augmentedPosts);
        setIsLoading(false);
      } catch (err) {
        setError('Failed to fetch posts');
        setIsLoading(false);
      }
    }, 500);

    return () => {
      isMounted = false;
      clearTimeout(timer);
    };
  }, [type, radius, userLocation?.latitude, userLocation?.longitude]);

  return { posts, isLoading, error };
};
