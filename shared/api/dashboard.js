import apiClient from './client';

const base = '/dashboard';

export async function getDashboardData(params) {
    const { data } = await apiClient.get(base, { params });
    return data;
}
