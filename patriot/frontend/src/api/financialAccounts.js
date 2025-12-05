import apiClient from '../../../shared/api/client';

const base = '/financial-accounts';

export async function listFinancialAccounts() {
    const { data } = await apiClient.get(base);
    return data;
}

export async function createFinancialAccount(payload) {
    const { data } = await apiClient.post(base, payload);
    return data;
}

export async function getFinancialAccount(id) {
    const { data } = await apiClient.get(`${base}/${id}`);
    return data;
}

export async function updateFinancialAccount(id, payload) {
    const { data } = await apiClient.put(`${base}/${id}`, payload);
    return data;
}

export async function deleteFinancialAccount(id) {
    const { data } = await apiClient.delete(`${base}/${id}`);
    return data;
}
