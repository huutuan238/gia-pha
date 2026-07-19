import apiClient from "./axios";

export const getAllEvent = () => {
  return apiClient.get("/event");
};

export const addEvent = (eventInfo) => {
  return apiClient.post(`/event`, eventInfo);
};
