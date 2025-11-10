import { useTheme } from '@/theme';
import { Tabs } from "expo-router"
import React, {useEffect} from "react"
import {Ionicons} from "@expo/vector-icons"

const DashboardLayout = () => {
  const colors = useTheme();
    const iconSize = 30

  return (
    <Tabs
      screenOptions={{
        animation: "fade",
        headerShown: false,
        tabBarShowLabel: false,
        tabBarStyle: {
          backgroundColor: colors.card,
          borderRadius: 8,
          position: 'absolute',
          overflow:'hidden',
          left: 0,
          bottom: 0,
          right: 0,
          paddingBottom:-3,
          height: 70
        },
        tabBarIconStyle: {
          marginTop: 13
        }


    }}
    >
    <Tabs.Screen
      name="Map"
      options = {{tabBarIcon: ({focused}) => (
        <Ionicons
          size= {iconSize}
          name={focused ? "map" : "map-outline"}
          color={focused ? colors.primary : colors.foreground}
        />
      )}}
    />

    <Tabs.Screen
      name="Feed"
      options = {{tabBarIcon: ({focused}) => (
        <Ionicons
          size= {iconSize}
          name={focused ? "albums" : "albums-outline"}
          color={focused ? colors.primary : colors.foreground}
        />
      )}}
    />

    <Tabs.Screen
      name="Profile"
      options = {{tabBarIcon: ({focused}) => (
        <Ionicons
          size= {iconSize}
          name={focused ? "person" : "person-outline"}
          color={focused ? colors.primary : colors.foreground}
        />
      )}}
    />

    <Tabs.Screen
      name="Settings"
      options = {{tabBarIcon: ({focused}) => (
        <Ionicons
          size= {iconSize}
          name={focused ? "settings" : "settings-outline"}
          color={focused ? colors.primary : colors.foreground}
        />
      )}}
    />

    </Tabs>
  )}

export default DashboardLayout
