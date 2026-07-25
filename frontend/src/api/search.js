import apiClient from "./axios";

export const getPersonLineageStats = (person_id) => {
  return apiClient.post("/search/person-info/", person_id);
};