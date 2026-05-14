import axios from 'axios';

// Use environment variable if available, otherwise fall back to production URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://testimony-api.onrender.com';

console.log('API Base URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

export const uploadRecording = async (questionNum, blob) => {
  const response = await axios.post(
    `${API_BASE_URL}/upload_recording/${questionNum}`,
    blob,
    {
      headers: {
        'Content-Type': 'application/octet-stream',
      },
    }
  );
  return response.data;
};

export const getRecentResults = async () => {
  const response = await api.get('/recent');
  return response.data;
};

export const getAnalysisById = async (itemId) => {
  const response = await api.get(`/analysis/${itemId}`);
  return response.data;
};

export const generateReport = async (analysisData) => {
  const response = await api.post('/generate_report', {
    analysis_data: analysisData,
  });
  return response.data;
};

export default api;
