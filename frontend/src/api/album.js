import apiClient from "./axios";

export const getAlbums = () => {
  return apiClient.get("/albums");
};

export const getAlbumDetail = (albumId) => {
  return apiClient.get(`/albums/${albumId}`);
};

export const createAlbum = (album) => {
  return apiClient.post("/albums", album);
};

export const updateAlbum = (albumId, album) => {
  return apiClient.put(`/albums/${albumId}`, album);
};

export const deleteAlbum = (albumId) => {
  return apiClient.delete(`/albums/${albumId}`);
};

// file: đối tượng File lấy từ <input type="file"> hoặc event kéo-thả
// extra: { caption, takenDate } (tuỳ chọn)
export const uploadPhoto = (albumId, file, extra = {}) => {
  const formData = new FormData();
  formData.append("file", file);
  if (extra.caption) formData.append("caption", extra.caption);
  if (extra.takenDate) formData.append("takenDate", extra.takenDate);

  return apiClient.post(`/albums/${albumId}/photos`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const renamePhoto = (photoId, caption) => {
  return apiClient.put(`/photos/${photoId}`, { caption });
};

export const deletePhoto = (photoId) => {
  return apiClient.delete(`/photos/${photoId}`);
};

const BACKEND_ORIGIN = import.meta.env.VITE_API_ORIGIN

export const resolvePhotoUrl = (url) => {
  if (!url) return "";
  if (url.startsWith("http://") || url.startsWith("https://")) return url;
  return `${BACKEND_ORIGIN}${url}`;
};
