import apiClient from "./axios";

export const getAllContribution = () => {
    return Promise.resolve({
        data: [
          {
            id: "c1a2b3c4-1111-4aaa-9999-000000000001",
            title: "Đóng góp xây nhà thờ họ 2026",
            description: "Quỹ xây dựng, tu sửa nhà thờ họ Nguyễn Hữu đợt 1 năm 2026.",
            excelUrl: "https://gia-pha-images.s3.us-east-1.amazonaws.com/contributions/xay-nha-tho-2026.xlsx",
            eventDate: "2026-03-15",
            createdAt: "2026-03-01T08:00:00",
          },
          {
            id: "c1a2b3c4-2222-4bbb-9999-000000000002",
            title: "Công đức giỗ tổ 2025",
            description: "Danh sách con cháu đóng góp cho lễ giỗ tổ hằng năm.",
            excelUrl: "https://gia-pha-images.s3.us-east-1.amazonaws.com/contributions/gio-to-2025.xlsx",
            eventDate: "2025-08-20",
            createdAt: "2025-08-05T09:30:00",
          },
        ],
      });
//   return apiClient.get("/contributions");
};

export const getContributionById = (id) => {
    return Promise.resolve({
        data: 
          {
            id: "c1a2b3c4-2222-4bbb-9999-000000000002",
            title: "Công đức giỗ tổ 2025",
            description: "Danh sách con cháu đóng góp cho lễ giỗ tổ hằng năm.",
            excelUrl: "https://docs.google.com/spreadsheets/d/1BUMh3qar4ZL7ytmBnYdlktZaUv81REyZ/edit?usp=sharing&ouid=115544203726347606869&rtpof=true&sd=true",
            eventDate: "2025-08-20",
            createdAt: "2025-08-05T09:30:00",
          },
      });
  return apiClient.get(`/contributions/${id}`);
};

export const addContribution = (info) => {
  return apiClient.post("/contributions", info);
};

export const updateContribution = (id, info) => {
  return apiClient.put(`/contributions/${id}`, info);
};

export const deleteContribution = (id) => {
  return apiClient.delete(`/contributions/${id}`);
};