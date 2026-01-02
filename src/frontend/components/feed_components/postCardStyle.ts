import { StyleSheet } from "react-native";

export const styles = StyleSheet.create({
  card: {
    paddingVertical: 16,
    paddingHorizontal: 12,
    borderWidth: 1,
    borderRadius: 12,
    marginVertical: 8,
    marginHorizontal: 12,
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
    elevation: 2,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
  },
  avatar: {
    width: 42,
    height: 42,
    borderRadius: 21,
    marginRight: 10,
  },
  username: {
    fontWeight: "600",
    fontSize: 15,
  },
  location: {
    fontSize: 12,
  },
  text: {
    fontSize: 15,
    lineHeight: 20,
    marginBottom: 8,
  },
  image: {
    width: "100%",
    height: 320,
    borderRadius: 12,
    marginVertical: 8,
  },
  actions: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: 8,
    gap: 16,
  },
  action: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  count: {
    fontSize: 13,
  },
});
