import apiClient from "./axios";

export const getFamilyTree = () => {
  return apiClient.get("/family-tree");
};

export const addPerson = (person) => {
  return apiClient.post("/persons", person);
};

export const updatePerson = (id, person) => {
  return apiClient.put(`/persons/${id}`, person);
};

export const deletePerson = (id) => {
  return apiClient.delete(`/persons/${id}`);
};
