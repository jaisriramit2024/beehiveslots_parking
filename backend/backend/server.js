import express from "express";
import cors from "cors";
import http from "http";
import slotRoutes from "./routes/slots.js";
import bookingRoutes from "./routes/bookings.js";
import paymentRoutes from "./routes/payments.js";
import setupWS from "./websocket.js";

const app = express();
app.use(cors());
app.use(express.json());

app.use("/slots", slotRoutes);
app.use("/bookings", bookingRoutes);
app.use("/payments", paymentRoutes);

const server = http.createServer(app);
setupWS(server);

server.listen(4000, () =>
  console.log("Beehive backend running on port 4000")
);
