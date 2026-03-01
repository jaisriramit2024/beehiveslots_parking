import { Router } from "express";
const router = Router();

router.post("/", (req, res) => {
  res.json({
    status: "success",
    transactionId: Date.now()
  });
});

export default router;
