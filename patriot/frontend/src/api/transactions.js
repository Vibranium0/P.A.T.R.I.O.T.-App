const base = "/api/transactions";

export async function createTransaction(payload) {
  const r = await fetch(base, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) {
    const txt = await r.text();
    throw new Error(txt || "failed");
  }
  return r.json();
}
