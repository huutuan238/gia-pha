import apiClient from "./axios";

export const registerUser = (registerInfo) => {
  return apiClient.post("/auth/register", registerInfo);
};

export const loginUser = (loginInfo) => {
  return apiClient.post("/auth/login", loginInfo);
};

export const getCurrentUser = () => {
  return apiClient.get("/auth/me");
};