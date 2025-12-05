import apiClient from './client';

const base = '/households';

export async function listHouseholds() {
    const { data } = await apiClient.get(base);
    return data;
}

export async function getHousehold(id) {
    const { data } = await apiClient.get(`${base}/${id}`);
    return data;
}

export async function createHousehold(payload) {
    const { data } = await apiClient.post(base, payload);
    return data;
}

export async function updateHousehold(id, payload) {
    const { data } = await apiClient.put(`${base}/${id}`, payload);
    return data;
}

export async function deleteHousehold(id) {
    const { data } = await apiClient.delete(`${base}/${id}`);
    return data;
}
