import React from 'react';
import { Image, View } from 'react-native';
import { cn } from '../../lib/utils'; // Assuming cn utility is available for NativeWind

interface AvatarProps {
  source: string; // URL for the avatar image
  size?: 'sm' | 'md' | 'lg' | 'xl'; // Added 'xl' for larger profile size
  alt?: string;
  className?: string; // For additional Tailwind classes
}

const Avatar: React.FC<AvatarProps> = ({ source, size = 'md', alt = 'User Avatar', className }) => {
  const avatarSizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-10 w-10',
    lg: 'h-12 w-12',
    xl: 'h-32 w-32', // Matches the size in Profile.tsx
  };

  const borderAndShadowClasses = size === 'xl' ? 'border-4 border-card bg-card shadow-lg' : '';

  return (
    <View className={cn('rounded-full overflow-hidden', avatarSizeClasses[size], borderAndShadowClasses, className)}>
      <Image source={{ uri: source }} accessibilityLabel={alt} className="h-full w-full" resizeMode="cover" />
    </View>
  );
};

export { Avatar };
