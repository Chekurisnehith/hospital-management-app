import React from "react";
import { View, Text, Button, StyleSheet } from "react-native";

export default function DoctorCard({ doctor, onEdit, onDelete }) {
  return (
    <View style={styles.card}>
      <Text style={styles.text}>Name: {doctor.name}</Text>
      <Text style={styles.text}>Specialty: {doctor.specialty}</Text>
      <Text style={styles.text}>Contact: {doctor.contact}</Text>
      <View style={styles.actions}>
        <Button title="Edit" onPress={onEdit} />
        <Button title="Delete" color="red" onPress={onDelete} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: { 
    borderWidth: 1, 
    padding: 15, 
    marginVertical: 10, 
    borderRadius: 8,
    backgroundColor: "rgba(255, 255, 255, 0.9)",
    borderColor: "#ddd",
  },
  text: { 
    marginBottom: 5,
    fontSize: 16,
  },
  actions: { 
    flexDirection: "row", 
    justifyContent: "space-between",
    marginTop: 10,
  },
});