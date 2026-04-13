CREATE TABLE shipments (
  id SERIAL PRIMARY KEY,
  shipment_id VARCHAR(50) UNIQUE NOT NULL,
  origin VARCHAR(100) NOT NULL,
  destination VARCHAR(100) NOT NULL,
  current_lat DECIMAL(9,6) NOT NULL,
  current_lng DECIMAL(9,6) NOT NULL,
  status VARCHAR(50) NOT NULL,
  cargo_type VARCHAR(50) NOT NULL
);