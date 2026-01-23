import axios from 'axios';


const apiClient = axios.create({
  baseURL: '/api',
  // withCredentials: true, // Not needed, no cookies for auth
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token from localStorage to every request
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('sentinel_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error));

export default apiClient;
