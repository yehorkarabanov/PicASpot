import React from "react";
import { View, Text, Image, Pressable } from "react-native";
import { Feather } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import { useTheme } from "@/theme";
import { styles } from "./postCardStyle";

export type Comment = {
  id: number;
  username: string;
  avatar: string;
  comment: string;
  likes: number;
};

type PostCardProps = {
  postId: string | number;
  username: string;
  avatar: string;
  text: string;
  image: string;
  location: string;
  likes: number;
  comments_nr: number;
  comments?: Comment[];
};

export const PostCard: React.FC<PostCardProps> = ({
  postId,
  username,
  avatar,
  text,
  image,
  location,
  likes,
  comments_nr,
  comments,
}) => {
  const colors = useTheme();
  const router = useRouter();

  return (
    <Pressable
      onPress={() =>
        router.push({
          pathname: "/post/[id]",
          params: { id: postId },
        })
      }
    >
      <View
        style={[
          styles.card,
          { backgroundColor: colors.card, borderColor: colors.border },
        ]}
      >
        {/* Header */}
        <View style={styles.header}>
          <Image source={{ uri: avatar }} style={styles.avatar} />
          <View>
            <Text style={[styles.username, { color: colors.cardForeground }]}>
              {username}
            </Text>
            <Text style={[styles.location, { color: colors.mutedForeground }]}>
              {location}
            </Text>
          </View>
        </View>

        {/* Post Text */}
        <Text style={[styles.text, { color: colors.cardForeground }]}>{text}</Text>

        {/* Post Image */}
        <Image source={{ uri: image }} style={styles.image} />

        {/* Actions */}
        <View style={styles.actions}>
          <View style={styles.action}>
            <Feather name="heart" size={20} color={colors.cardForeground} />
            <Text style={[styles.count, { color: colors.cardForeground }]}>{likes}</Text>
          </View>
          <View style={styles.action}>
            <Feather name="message-circle" size={20} color={colors.cardForeground} />
            <Text style={[styles.count, { color: colors.cardForeground }]}>
              {comments_nr}
            </Text>
          </View>
        </View>
      </View>
    </Pressable>
  );
};
