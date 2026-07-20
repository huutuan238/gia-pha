import apiClient from "./axios";

export const getAllUser = () => {
  return apiClient.get("/users");
};

export const updateUserRole = (id, role) => {
  return apiClient.put(`/users/${id}/role`, { role });
};