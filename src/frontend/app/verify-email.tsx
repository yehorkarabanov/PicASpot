import * as React from 'react';
import { View } from 'react-native';
import { Stack, useRouter } from 'expo-router';
import { Text } from '@/components/ui/text';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';

export default function VerifyEmailScreen() {
  const { refreshUser } = useAuth();
  const router = useRouter();
  const [isSending, setIsSending] = React.useState(false);
  const [message, setMessage] = React.useState<string | null>(null);

  const handleResend = async () => {
    setIsSending(true);
    setMessage(null);
    try {
      // try best-effort resend endpoint using the configured API client
      // The backend may expose an endpoint like /v1/auth/resend-verification — adapt if different
      const res = await api.post('/v1/auth/resend-verification');
      if (res.status >= 200 && res.status < 300) {
        setMessage('Verification email resent. Please check your inbox.');
      } else {
        setMessage('Unable to resend verification from client. Please check your email or try again later.');
      }
    } catch (err) {
      setMessage('Failed to contact server to resend verification.');
    } finally {
      setIsSending(false);
    }
  };

  const handleIHaveVerified = async () => {
    setMessage(null);
    try {
      await refreshUser();
      router.replace('/');
    } catch (err) {
      setMessage('Unable to verify status yet — please try again in a moment.');
    }
  };

  return (
    <View className="flex-1 justify-center px-6 py-12">
      <Stack.Screen options={{ title: 'Verify Email', headerShown: false }} />
      <View className="mb-6">
        <Text className="text-3xl font-bold mb-2">Verify your email</Text>
        <Text className="text-base text-muted-foreground">
          We've sent a verification link to the email address you provided. Open that email and follow the
          link to activate your account.
        </Text>
      </View>

      {message ? (
        <View className="mb-4">
          <Text className="text-sm text-muted-foreground">{message}</Text>
        </View>
      ) : null}

      <View className="gap-3">
        <Button onPress={handleResend} disabled={isSending} className="mb-2">
          <Text>{isSending ? 'Sending...' : 'Resend verification email'}</Text>
        </Button>

        <Button variant="secondary" onPress={handleIHaveVerified}>
          <Text>I have verified — continue</Text>
        </Button>
      </View>
    </View>
  );
}
