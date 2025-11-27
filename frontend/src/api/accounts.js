// lightweight frontend API helpers for accounts
const base = "/api/accounts";

export async function listAccounts() {
    const r = await fetch(base + "/list");
    if (!r.ok) throw new Error("failed");
    return r.json();
}
