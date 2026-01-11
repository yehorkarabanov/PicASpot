import '@/global.css';
import * as SystemUI from 'expo-system-ui';
import { NAV_THEME } from '@/lib/theme';
import { AuthProvider } from '@/contexts/AuthContext';
import { ThemeProvider } from '@react-navigation/native';
import { PortalHost } from '@rn-primitives/portal';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useColorScheme } from 'nativewind';
import { useTheme } from '@/theme';
import { LocationProvider } from '@/contexts/LocationContext';

export {
  ErrorBoundary,
} from 'expo-router';

export default function RootLayout() {
  const colors = useTheme();
  const { colorScheme } = useColorScheme();
  SystemUI.setBackgroundColorAsync(colors.background);

  return (
    <ThemeProvider value={NAV_THEME[colorScheme ?? 'light']}>
      <AuthProvider>
        <LocationProvider>
          <StatusBar style={colorScheme === 'dark' ? 'light' : 'dark'} />
          <Stack>
            <Stack.Screen name="(dashboard)" options={{ headerShown: false }} />
          </Stack>
          <PortalHost />
        </LocationProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
