// Minimal Express app used as a test fixture for tracedocs.
const express = require("express");

const app = express();
const port = process.env.PORT || 3000;
const databaseUrl = process.env.DATABASE_URL;
const stripeKey = process.env.STRIPE_SECRET_KEY;

app.get("/health", (req, res) => {
  res.json({ ok: true, db: Boolean(databaseUrl), payments: Boolean(stripeKey) });
});

function listUsers(req, res) {
  res.json([]);
}

app.get("/users", listUsers);

app.post("/users", (req, res) => {
  res.status(201).json({});
});

app.listen(port, () => {
  console.log(`sample-node-app listening on ${port}`);
});
