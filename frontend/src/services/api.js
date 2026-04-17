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
  return response.data.data;
};

export const generateTriage = async (shipment, risk) => {
  const payload = {
    shipment_id: shipment.shipment_id,

    risk_context:
      risk?.risk_details?.description || "Risk detected near shipment route.",

    cargo_type: shipment.cargo_type,
    cargo_value: shipment.cargo_value ?? 500000,
    original_eta:
      shipment.original_eta ??
      new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
    status: shipment.status,

    current_location: {
      lat: Number(shipment.current_lat),
      lng: Number(shipment.current_lng),
      name: shipment.origin || "Current Origin",
    },

    destination: {
      lat: Number(shipment.destination_lat),
      lng: Number(shipment.destination_lng),
      name: shipment.destination || "Destination",
    },

    risk_details: risk?.risk_details || null,

    // broad helpful fallback until your friend gives real ports from DB
    available_ports: shipment.available_ports ?? [
      {
        lat: Number(shipment.destination_lat),
        lng: Number(shipment.destination_lng),
        name: shipment.destination || "Primary Destination",
      },
    ],
  };

  const response = await axios.post(`${API_BASE_URL}/generate-triage`, payload);
  return response.data.data;
};
