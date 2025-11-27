// lightweight frontend API helpers; adjust base url if needed
const base = "/api/funds";

export async function listFunds() {
  const r = await fetch(base);
  if (!r.ok) throw new Error("failed");
  return r.json();
}

export async function createFund(payload) {
  const r = await fetch(base, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error("failed to create fund");
  return r.json();
}

export async function updateFund(id, payload) {
  const r = await fetch(`${base}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error("failed to update fund");
  return r.json();
}
