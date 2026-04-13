import db from "../config/db.js";

const seedShipments = async () => {
  try {
    await db.connect();

    await db.query("DELETE FROM shipments");

    await db.query(`
      INSERT INTO shipments (shipment_id, origin, destination, current_lat, current_lng, status, cargo_type)
      VALUES
      ('SHP-1001', 'Shanghai, China', 'Rotterdam, Netherlands', 28.6139, 77.2090, 'in_transit', 'electronics'),
      ('SHP-1002', 'Singapore', 'Dubai, UAE', 15.8700, 100.9925, 'in_transit', 'medical'),
      ('SHP-1003', 'Hamburg, Germany', 'New York, USA', 50.1109, 8.6821, 'delayed', 'automotive'),
      ('SHP-1004', 'Mumbai, India', 'Jeddah, Saudi Arabia', 23.8859, 45.0792, 'at_port', 'food'),
      ('SHP-1005', 'Los Angeles, USA', 'Tokyo, Japan', 36.2048, 138.2529, 'in_transit', 'retail'),
      ('SHP-1006', 'Alexandria, Egypt', 'Athens, Greece', 33.9391, 35.2137, 'rerouted', 'electronics'),
      ('SHP-1007', 'Busan, South Korea', 'San Francisco, USA', 35.6762, 139.6503, 'in_transit', 'automotive'),
      ('SHP-1008', 'Durban, South Africa', 'Mumbai, India', -1.2921, 36.8219, 'delayed', 'food'),
      ('SHP-1009', 'Santos, Brazil', 'Lisbon, Portugal', -14.2350, -51.9253, 'in_transit', 'retail'),
      ('SHP-1010', 'Hong Kong', 'Sydney, Australia', -6.2088, 106.8456, 'at_port', 'electronics');
    `);

    console.log("Seed data inserted successfully");
  } catch (error) {
    console.error("Error seeding shipments:", error);
  } finally {
    await db.end();
  }
};

seedShipments();
