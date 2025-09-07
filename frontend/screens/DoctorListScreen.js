import React, { useEffect, useState } from "react";
import {
  View,
  Button,
  FlatList,
  Alert,
  StyleSheet,
  TouchableOpacity,
  Text,
  ImageBackground,
} from "react-native";
import { api } from "../api";
import DoctorCard from "../components/DoctorCard";

export default function DoctorListScreen({ navigation, onLogout }) {
  const [doctors, setDoctors] = useState([]);

  const fetchDoctors = async () => {
    try {
      const res = await api.get("/doctors");
      setDoctors(res.data);
    } catch (err) {
      Alert.alert("Error", "Failed to fetch doctors");
    }
  };

  useEffect(() => {
    const unsubscribe = navigation.addListener("focus", fetchDoctors);
    return unsubscribe;
  }, [navigation]);

  const deleteDoctor = async (id) => {
    try {
      await api.delete(`/doctors/${id}`);
      fetchDoctors();
    } catch {
      Alert.alert("Error", "Failed to delete doctor");
    }
  };

  return (
    <ImageBackground
      source={require("../assets/docback.png")}
      style={styles.background}
      resizeMode="cover"
    >
      <View style={styles.overlay} />

      <View style={styles.container}>
        <View style={styles.topBar}>
          <Button
            title="Add Doctor"
            onPress={() =>
              navigation.navigate("DoctorForm", { mode: "add" })
            }
            color="#007BFF"
          />

          <TouchableOpacity style={styles.logoutBtn} onPress={onLogout}>
            <Text style={styles.logoutText}>Logout</Text>
          </TouchableOpacity>
        </View>

        <FlatList
          data={doctors}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <DoctorCard
              doctor={item}
              onEdit={() =>
                navigation.navigate("DoctorForm", {
                  mode: "edit",
                  doctor: item,
                })
              }
              onDelete={() => deleteDoctor(item.id)}
            />
          )}
        />
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  background: {
    flex: 1,
    width: "100%",
    height: "100%",
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "rgba(255, 255, 255, 0.7)",
  },
  container: {
    flex: 1,
    padding: 16,
  },
  topBar: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 15,
    marginTop: 5,
  },
  logoutBtn: {
    backgroundColor: "#ff4d4d",
    paddingVertical: 7,
    paddingHorizontal: 14,
    borderRadius: 8,
    elevation: 3,
  },
  logoutText: {
    color: "#fff",
    fontWeight: "bold",
  },
});