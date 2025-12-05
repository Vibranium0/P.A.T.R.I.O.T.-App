import apiClient from '../../../shared/api/client';

const base = '/bills';

export async function listBills() {
    const { data } = await apiClient.get(base);
    return data;
}

export async function createBill(payload) {
    const { data } = await apiClient.post(base, payload);
    return data;
}

export async function updateBill(id, payload) {
    const { data } = await apiClient.put(`${base}/${id}`, payload);
    return data;
}

export async function deleteBill(id) {
    const { data } = await apiClient.delete(`${base}/${id}`);
    return data;
}

export async function markBillPaid(id) {
    const { data } = await apiClient.post(`${base}/${id}/pay`);
    return data;
}

export async function getBillSchedule(params) {
    const { data } = await apiClient.get(`${base}/schedule`, { params });
    return data;
}

export async function getUpcomingBills(days = 7) {
    const { data } = await apiClient.get(`${base}/upcoming`, { params: { days } });
    return data;
}

export async function getBillCategories() {
    const { data } = await apiClient.get(`${base}/categories`);
    return data;
}
