import { Router } from "express";
const router = Router();

let slots = [
  { id: 1, name: "Hive Prime", status: "available" },
  { id: 2, name: "Amber Bay", status: "occupied" }
];

router.get("/", (_, res) => res.json(slots));

router.post("/toggle/:id", (req, res) => {
  const slot = slots.find(s => s.id == req.params.id);
  slot.status =
    slot.status === "available" ? "occupied" : "available";
  res.json(slot);
});

export default router;
