import apiClient from '../../../shared/api/client';

const base = '/reports';

export async function getSummary() {
    const { data } = await apiClient.get(`${base}/summary`);
    return data;
}

export async function getForecast(params) {
    const { data } = await apiClient.get(`${base}/forecast`, { params });
    return data;
}

export async function getUpcomingBills(params) {
    const { data } = await apiClient.get(`${base}/upcoming-bills`, { params });
    return data;
}

export async function getFinancialHealth(params) {
    const { data } = await apiClient.get(`${base}/financial-health`, { params });
    return data;
}

export async function getIncomeBreakdown(params) {
    const { data } = await apiClient.get(`${base}/income-breakdown`, { params });
    return data;
}

export async function getDebtBreakdown(params) {
    const { data } = await apiClient.get(`${base}/debt-breakdown`, { params });
    return data;
}
