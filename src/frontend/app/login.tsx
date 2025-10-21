import * as React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Text } from '@/components/ui/text';
import { useAuth } from '@/contexts/AuthContext';
import { Link, Stack, useRouter } from 'expo-router';
import { AlertCircle } from 'lucide-react-native';
import { Alert, KeyboardAvoidingView, Platform, ScrollView, View } from 'react-native';

export default function LoginScreen() {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState('');

  const { login } = useAuth();
  const router = useRouter();

  const handleLogin = async () => {
    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      await login({ username: email, password });
      router.replace('/');
    } catch (err: any) {
      console.error('Login error:', err);

      // Better error handling
      let message = 'Invalid email or password';

      if (err.code === 'ECONNABORTED' || err.message === 'Network Error') {
        message =
          'Cannot connect to server. Please check your network connection and API URL.';
      } else if (err.response?.status === 400) {
        message = 'Invalid email or password';
      } else if (err.response?.data?.detail) {
        message = err.response.data.detail;
      }

      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Stack.Screen
        options={{
          title: 'Login',
          headerShown: false,
        }}
      />
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        className="flex-1">
        <ScrollView
          contentContainerClassName="flex-1"
          keyboardShouldPersistTaps="handled">
          <View className="flex-1 justify-center px-6 py-12">
            <View className="mb-8">
              <Text className="text-4xl font-bold mb-2">Welcome Back</Text>
              <Text className="text-lg text-muted-foreground">
                Sign in to continue
              </Text>
            </View>

            <View className="gap-4">
              {error ? (
                <View className="flex-row items-center gap-2 bg-destructive/10 p-4 rounded-lg border border-destructive/20">
                  <AlertCircle className="text-destructive" size={20} />
                  <Text className="text-destructive flex-1">{error}</Text>
                </View>
              ) : null}

              <View className="gap-2">
                <Text className="text-sm font-medium">Email</Text>
                <Input
                  placeholder="Enter your email"
                  value={email}
                  onChangeText={setEmail}
                  autoCapitalize="none"
                  keyboardType="email-address"
                  autoComplete="email"
                  editable={!isLoading}
                />
              </View>

              <View className="gap-2">
                <Text className="text-sm font-medium">Password</Text>
                <Input
                  placeholder="Enter your password"
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry
                  autoCapitalize="none"
                  autoComplete="password"
                  editable={!isLoading}
                />
              </View>

              <Button
                onPress={handleLogin}
                disabled={isLoading}
                className="mt-2">
                <Text>{isLoading ? 'Signing in...' : 'Sign In'}</Text>
              </Button>

              <View className="flex-row justify-center items-center gap-2 mt-4">
                <Text className="text-muted-foreground">
                  Don't have an account?
                </Text>
                <Link href="/register" asChild>
                  <Button variant="ghost" size="sm">
                    <Text>Sign Up</Text>
                  </Button>
                </Link>
              </View>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </>
  );
}
