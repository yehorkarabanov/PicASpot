import * as React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Text } from '@/components/ui/text';
import { useAuth } from '@/contexts/AuthContext';
import { Link, Stack, useRouter } from 'expo-router';
import { AlertCircle, CheckCircle } from 'lucide-react-native';
import { KeyboardAvoidingView, Platform, ScrollView, View } from 'react-native';

export default function RegisterScreen() {
  const [username, setUsername] = React.useState('');
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [confirmPassword, setConfirmPassword] = React.useState('');
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState('');

  const { register, needsEmailVerification } = useAuth();
  const router = useRouter();

  const validatePassword = (pwd: string) => {
    if (pwd.length < 8) {
      return 'Password must be at least 8 characters';
    }
    return '';
  };

  const handleRegister = async () => {
    if (!username || !email || !password || !confirmPassword) {
      setError('Please fill in all fields');
      return;
    }

    const passwordError = validatePassword(password);
    if (passwordError) {
      setError(passwordError);
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      await register({ username, email, password });

      // If registration requires email verification, redirect to verify screen
      if (needsEmailVerification) {
        router.replace({ pathname: '/verify-email' });
        return;
      }

      // otherwise go to home
      router.replace('/');
    } catch (err: any) {
      console.error('Registration error:', err);

      // Better error handling
      let message = 'Registration failed. Please try again.';

      if (err.code === 'ECONNABORTED' || err.message === 'Network Error') {
        message = 'Cannot connect to server. Please check your network connection and API URL.';
      } else if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        message = typeof detail === 'string' ? detail : 'Email or username already registered';
      }

      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const passwordStrength = password.length >= 8;

  return (
    <>
      <Stack.Screen
        options={{
          title: 'Register',
          headerShown: false,
        }}
      />
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        className="flex-1">
        <ScrollView contentContainerClassName="flex-1" keyboardShouldPersistTaps="handled">
          <View className="flex-1 justify-center px-6 py-12">
            <View className="mb-8">
              <Text className="mb-2 text-4xl font-bold">Create Account</Text>
              <Text className="text-lg text-muted-foreground">Sign up to get started</Text>
            </View>

            <View className="gap-4">
              {error ? (
                <View className="flex-row items-center gap-2 rounded-lg border border-destructive/20 bg-destructive/10 p-4">
                  <AlertCircle className="text-destructive" size={20} />
                  <Text className="flex-1 text-destructive">{error}</Text>
                </View>
              ) : null}

              <View className="gap-2">
                <Text className="text-sm font-medium">Username</Text>
                <Input
                  placeholder="Choose a username"
                  value={username}
                  onChangeText={setUsername}
                  autoCapitalize="none"
                  autoComplete="username"
                  editable={!isLoading}
                />
              </View>

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
                  placeholder="Create a password"
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry
                  autoCapitalize="none"
                  autoComplete="password-new"
                  editable={!isLoading}
                />
                {password.length > 0 && (
                  <View className="flex-row items-center gap-2">
                    <CheckCircle
                      size={16}
                      className={passwordStrength ? 'text-green-500' : 'text-muted-foreground'}
                    />
                    <Text
                      className={
                        passwordStrength
                          ? 'text-xs text-green-500'
                          : 'text-xs text-muted-foreground'
                      }>
                      At least 8 characters
                    </Text>
                  </View>
                )}
              </View>

              <View className="gap-2">
                <Text className="text-sm font-medium">Confirm Password</Text>
                <Input
                  placeholder="Confirm your password"
                  value={confirmPassword}
                  onChangeText={setConfirmPassword}
                  secureTextEntry
                  autoCapitalize="none"
                  autoComplete="password-new"
                  editable={!isLoading}
                />
              </View>

              <Button onPress={handleRegister} disabled={isLoading} className="mt-2">
                <Text>{isLoading ? 'Creating account...' : 'Sign Up'}</Text>
              </Button>

              <View className="mt-4 flex-row items-center justify-center gap-2">
                <Text className="text-muted-foreground">Already have an account?</Text>
                <Link href="/login" asChild>
                  <Button variant="ghost" size="sm">
                    <Text>Sign In</Text>
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
