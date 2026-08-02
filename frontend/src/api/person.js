import apiClient from "./axios";

export const getAllPerson = () => {
    return apiClient.get("/family-tree");
  };

export const searchPersons = (params) => {
    return apiClient.get("/search/person", {params});
  };