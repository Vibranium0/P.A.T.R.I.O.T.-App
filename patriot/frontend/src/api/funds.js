import apiClient from '../../../shared/api/client';

const base = '/funds';

export async function listFunds() {
  const { data } = await apiClient.get(base);
  return data;
}

export async function createFund(payload) {
  const { data } = await apiClient.post(base, payload);
  return data;
}

export async function updateFund(id, payload) {
  const { data } = await apiClient.patch(`${base}/${id}`, payload);
  return data;
}
