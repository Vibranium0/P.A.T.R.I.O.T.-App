import apiClient from '../../../shared/api/client';

const base = '/debts';

export async function listDebts() {
    const { data } = await apiClient.get(base);
    return data;
}

export async function createDebt(payload) {
    const { data } = await apiClient.post(base, payload);
    return data;
}

export async function getDebt(id) {
    const { data } = await apiClient.get(`${base}/${id}`);
    return data;
}

export async function updateDebt(id, payload) {
    const { data } = await apiClient.put(`${base}/${id}`, payload);
    return data;
}

export async function deleteDebt(id) {
    const { data } = await apiClient.delete(`${base}/${id}`);
    return data;
}

export async function makeDebtPayment(id, amount) {
    const { data } = await apiClient.post(`${base}/${id}/payment`, { amount });
    return data;
}
