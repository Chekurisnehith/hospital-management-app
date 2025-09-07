import axios from "axios";


export const api = axios.create({
  baseURL: "http://10.251.8.169:8000", 
});


export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common["Authorization"];
  }
};