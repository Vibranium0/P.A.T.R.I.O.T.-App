import apiClient from '../../../shared/api/client';

// lightweight frontend API helpers for accounts
const base = '/accounts';

export async function listAccounts() {
    const { data } = await apiClient.get(base + '/list');
    return data;
}
