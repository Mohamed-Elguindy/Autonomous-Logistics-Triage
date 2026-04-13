import express from "express";
import { getAllShipments } from "../controllers/shipmentController.js";
const router = express.Router();
router.get("/", getAllShipments);

export default router;
