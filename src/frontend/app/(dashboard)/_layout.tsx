import { useTheme } from '@/theme';
import { Tabs } from 'expo-router';
import React from 'react';
import { Ionicons } from '@expo/vector-icons';
import { LandmarkProvider } from '@/contexts/LandmarkContext';

const DashboardLayout = () => {
  const colors = useTheme();
  const iconSize = 30;

  return (
    <LandmarkProvider>
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarShowLabel: false,
        tabBarStyle: {
          backgroundColor: colors.background,
          borderRadius: 25,
          position: 'absolute',
          overflow: 'hidden',
          margin: 8,
          paddingBottom: 0,
          height: 70,
          borderColor: colors.border,
          borderWidth: 1,
          elevation: 8,
          shadowColor: '#000',
          shadowOffset: {
            width: 0,
            height: 4,
          },
          shadowOpacity: 0.3,
          shadowRadius: 8,
        },
        tabBarIconStyle: {
          marginTop: 10,
        },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.foreground,
      }}>
      <Tabs.Screen
        name="Map"
        options={{
          tabBarIcon: ({ focused }) => (
            <Ionicons
              size={iconSize}
              name={focused ? 'map' : 'map-outline'}
              color={focused ? colors.primary : colors.foreground}
            />
          ),
        }}
      />

      <Tabs.Screen
        name="Feed"
        options={{
          tabBarIcon: ({ focused }) => (
            <Ionicons
              size={iconSize}
              name={focused ? 'albums' : 'albums-outline'}
              color={focused ? colors.primary : colors.foreground}
            />
          ),
        }}
      />

      <Tabs.Screen
        name="Profile"
        options={{
          tabBarIcon: ({ focused }) => (
            <Ionicons
              size={iconSize}
              name={focused ? 'person' : 'person-outline'}
              color={focused ? colors.primary : colors.foreground}
            />
          ),
        }}
      />

      <Tabs.Screen
        name="Settings"
        options={{
          tabBarIcon: ({ focused }) => (
            <Ionicons
              size={iconSize}
              name={focused ? 'settings' : 'settings-outline'}
              color={focused ? colors.primary : colors.foreground}
            />
          ),
        }}
      />
    </Tabs>
    </LandmarkProvider>
  );
};

export default DashboardLayout;
