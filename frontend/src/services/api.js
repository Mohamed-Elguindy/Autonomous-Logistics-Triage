import axios from "axios";

const API_BASE_URL = "http://localhost:5000";

export const getAllShipments = async () => {
  const response = await axios.get(`${API_BASE_URL}/api/shipments`);
  return response.data;
};
