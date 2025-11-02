import { Tabs } from "expo-router"

const DashboardLayout = () => {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          paddingTop: 10,
          height: 80,
        },
    }}
    />
  )}

export default DashboardLayout
