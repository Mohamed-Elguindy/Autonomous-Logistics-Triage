import dotenv from "dotenv";
import app from "./app.js";
import db from "./config/db.js";

dotenv.config();

const PORT = process.env.PORT || 5000;

db.connect()
  .then(() => {
    console.log("Connected to PostgreSQL");

    app.listen(PORT, () => {
      console.log(`Server is running on port ${PORT}`);
    });
  })
  .catch((err) => {
    console.error("Database connection failed:", err);
  });
