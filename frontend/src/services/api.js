import axios from "axios";

const API_BASE_URL = "http://localhost:5000/api/shipments";

export const getAllShipments = async () => {
  const response = await axios.get(API_BASE_URL);
  return response.data;
};

export const analyzeRisk = async (shipment) => {
  const payload = {
    shipment_id: shipment.shipment_id,
    current_location: {
      lat: Number(shipment.current_lat),
      lng: Number(shipment.current_lng),
    },
    destination: {
      lat: Number(shipment.destination_lat),
      lng: Number(shipment.destination_lng),
    },
    cargo_type: shipment.cargo_type,
  };

  const response = await axios.post(`${API_BASE_URL}/analyze-risk`, payload);
  return response.data;
};
