import { View } from "react-native"
import { Text } from "@/components/ui/text";
import { Stack } from 'expo-router';

const Profile = () => {

  return (
    <>
      <Stack.Screen options={{
        title: 'Feed',
      }}/>
      <View className="flex-1 items-center justify-center gap-8 p-4 bg-background">
        <View className="items-center gap-2">
          <Text className="text-2xl font-bold">Feed placeholder</Text>
        </View>
      </View>
    </>
  );
}

export default Profile;
