import apiClient from "./axios";

export const getPersonLineageStats = (person_id) => {
  return apiClient.post("/search/person-info/", person_id);
};

export function getRelationship(person1Id, person2Id) {
  return apiClient.get("/search/relationship", {
    params: { person1_id: person1Id, person2_id: person2Id },
  });
}