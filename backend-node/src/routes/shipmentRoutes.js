import express from "express";
import {
  getAllShipments,
  analyzeRisk,
  generateTriage,
} from "../controllers/shipmentController.js";

const router = express.Router();

router.get("/", getAllShipments);
router.post("/analyze-risk", analyzeRisk);
router.post("/generate-triage", generateTriage);

export default router;
