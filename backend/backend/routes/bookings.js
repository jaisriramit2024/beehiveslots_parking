import { Router } from "express";
const router = Router();

let bookings = [];

router.post("/", (req, res) => {
  const booking = {
    id: Date.now(),
    ...req.body,
    status: "confirmed"
  };
  bookings.push(booking);
  res.json(booking);
});

router.get("/", (_, res) => res.json(bookings));

export default router;
