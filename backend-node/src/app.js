import express from "express";
import cors from "cors";
import shipmentRoutes from "./routes/shipmentRoutes.js";
const app = express();

app.use(
  cors({
    origin: "http://localhost:5173",
  }),
);
app.use(express.json());

app.get("/health", (req, res) => {
  res.status(200).json({
    success: true,
    message: "Backend is running",
  });
});

app.use("/api/shipments", shipmentRoutes);

export default app;
