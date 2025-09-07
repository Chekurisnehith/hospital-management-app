import React, { useState } from "react";
import {
  View,
  TextInput,
  TouchableOpacity,
  Text,
  StyleSheet,
  Alert,
  ImageBackground,
  ScrollView,
} from "react-native";
import { api } from "../api";

export default function DoctorFormScreen({ route, navigation }) {
  const { mode, doctor } = route.params || {};
  const [name, setName] = useState(doctor?.name || "");
  const [specialty, setSpecialty] = useState(doctor?.specialty || "");
  const [contact, setContact] = useState(doctor?.contact || "");

  const handleSave = async () => {
    try {
      if (mode === "edit") {
        await api.put(`/doctors/${doctor.id}`, { name, specialty, contact });
      } else {
        await api.post("/doctors", { name, specialty, contact });
      }
      navigation.goBack();
    } catch (err) {
      Alert.alert("Error", "Failed to save doctor");
    }
  };

  return (
    <ImageBackground
      source={require("../assets/docform2.png")}
      style={styles.background}
      resizeMode="cover"
    >
      <View style={styles.overlay} />

      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.container}>
          <Text style={styles.header}>
            {mode === "edit" ? "Edit Doctor" : "Add Doctor"}
          </Text>

          <TextInput
            style={styles.input}
            placeholder="Name"
            value={name}
            onChangeText={setName}
            placeholderTextColor="#666"
          />

          <TextInput
            style={styles.input}
            placeholder="Specialty"
            value={specialty}
            onChangeText={setSpecialty}
            placeholderTextColor="#666"
          />

          <TextInput
            style={styles.input}
            placeholder="Contact"
            value={contact}
            onChangeText={setContact}
            placeholderTextColor="#666"
            keyboardType="phone-pad"
          />

          <TouchableOpacity style={styles.saveBtn} onPress={handleSave}>
            <Text style={styles.saveText}>Save</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
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
    backgroundColor: "rgba(255,255,255,0.2)",
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: "center",
    padding: 20,
  },
  container: {
    backgroundColor: "rgba(255,255,255,0.7)",
    padding: 20,
    borderRadius: 12,
    elevation: 4,
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowRadius: 5,
    shadowOffset: { width: 0, height: 2 },
  },
  header: {
    fontSize: 22,
    fontWeight: "bold",
    color: "#333",
    marginBottom: 20,
    textAlign: "center",
  },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    marginBottom: 15,
    padding: 12,
    borderRadius: 10,
    backgroundColor: "#fff",
    fontSize: 16,
    color: "#000",
    elevation: 2,
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 2 },
  },
  saveBtn: {
    backgroundColor: "#00796B",
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 10,
    elevation: 3,
  },
  saveText: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "600",
  },
});