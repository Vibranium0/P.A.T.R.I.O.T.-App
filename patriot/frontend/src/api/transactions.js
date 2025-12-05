import apiClient from '../../../shared/api/client';

const base = '/transactions';

export async function createTransaction(payload) {
  const { data } = await apiClient.post(base, payload);
  return data;
}
