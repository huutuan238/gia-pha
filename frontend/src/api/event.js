import apiClient from "./axios";

export const getAllEvent = () => {
  return apiClient.get("/events");
};

export const getEventById = (id) => {
  return apiClient.get(`/events/${id}`);
};

export const deleteEvent = (id) => {
  return apiClient.delete(`/events/${id}`);
};

export const addEvent = (eventInfo) => {
  return apiClient.post("/events", eventInfo);
};
