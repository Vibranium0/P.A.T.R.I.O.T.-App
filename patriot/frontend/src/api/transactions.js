import apiClient from './client.js';

const base = '/transactions';

export async function createTransaction(payload) {
  const { data } = await apiClient.post(base, payload);
  return data;
}
