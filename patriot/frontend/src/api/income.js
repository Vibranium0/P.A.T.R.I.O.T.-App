import apiClient from './client.js';

const base = '/income';

export async function listIncome(params) {
    const { data } = await apiClient.get(base, { params });
    return data;
}

export async function createIncome(payload) {
    const { data } = await apiClient.post(base, payload);
    return data;
}

export async function deleteIncome(id) {
    const { data } = await apiClient.delete(`${base}/${id}`);
    return data;
}

export async function getIncomeSummary(params) {
    const { data } = await apiClient.get(`${base}/summary`, { params });
    return data;
}
