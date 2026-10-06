import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const createQr = (contentUrl) =>
  api.post("/create-qr", null, {
    params: { content_url: contentUrl },
  });

export const updateQr = (qrId, destinationUrl) =>
  api.put(`/update-qr/${encodeURIComponent(qrId)}`, {
    destination_url: destinationUrl,
  });

export const getQrDetails = (qrId) =>
  api.get(`/details/${encodeURIComponent(qrId)}`);