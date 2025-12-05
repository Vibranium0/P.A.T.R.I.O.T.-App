import apiClient from './client';

const base = '/user';

export async function getUserProfile() {
    const { data } = await apiClient.get(base + '/profile');
    return data;
}

export async function updateUserProfile(payload) {
    const { data } = await apiClient.put(base + '/profile', payload);
    return data;
}
