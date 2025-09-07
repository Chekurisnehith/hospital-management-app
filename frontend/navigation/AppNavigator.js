import React, { useState } from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import RegisterScreen from "../screens/RegisterScreen";
import LoginScreen from "../screens/LoginScreen";
import DoctorListScreen from "../screens/DoctorListScreen";
import DoctorFormScreen from "../screens/DoctorFormScreen";
import { setAuthToken } from "../api";

const Stack = createNativeStackNavigator();

export default function AppNavigator() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLoginSuccess = (token) => {
    setAuthToken(token);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setAuthToken(null);
    setIsAuthenticated(false);
  };

  return (
    <NavigationContainer>
      <Stack.Navigator>
        {!isAuthenticated ? (
          <>
            <Stack.Screen name="Login">
              {(props) => (
                <LoginScreen {...props} onLoginSuccess={handleLoginSuccess} />
              )}
            </Stack.Screen>
            <Stack.Screen name="Register" component={RegisterScreen} />
          </>
        ) : (
          <>
            <Stack.Screen name="Doctors">
              {(props) => (
                <DoctorListScreen {...props} onLogout={handleLogout} />
              )}
            </Stack.Screen>
            <Stack.Screen name="DoctorForm" component={DoctorFormScreen} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}