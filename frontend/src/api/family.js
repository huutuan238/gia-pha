import apiClient from "./axios";

export const getAllFamily = () => {
  return apiClient.get("/families");
};

export const getFamilyById = (id) => {
  return apiClient.get(`/families/${id}`);
};

export const addFamily = (familyInfo) => {
  return apiClient.post("/families", familyInfo);
};

export const updateFamily = (id, familyInfo) => {
  return apiClient.put(`/families/${id}`, familyInfo);
};

export const deleteFamily = (id) => {
  return apiClient.delete(`/families/${id}`);
};
