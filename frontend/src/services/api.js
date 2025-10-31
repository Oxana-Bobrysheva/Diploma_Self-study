import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api/';

const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Auth endpoints
export const loginUser = (formData) => {
  const loginData = {
    email: formData.email,
    password: formData.password
  };
  console.log('API sending payload:', loginData);
  return api.post('/token/', loginData);
};

export const refreshToken = (data) => api.post('/token/refresh/', data);
export const registerUser = (data) => api.post('/users/signup/', data);

// LMS endpoints (new)
export const getCourses = () => api.get(`/courses/`);
export const getCourseDetails = (courseId) => api.get(`/courses/${courseId}/`);
export const getMyCourses = () => api.get(`/courses/my/`);
export const getMaterials = (courseId) => api.get(`/courses/${courseId}/materials/`);
export const getMaterialDetails = (materialId) => api.get(`/materials/${materialId}/`);
export const getTests = (courseId) => api.get(`/courses/${courseId}/tests/`);
export const getTestDetails = (testId) => api.get(`/tests/${testId}/`);
export const submitTestResult = (data) => api.post(`/test-results/`, data);


export const getTeachers = () => api.get(`/users/teachers/`);

export const addMaterial = (courseId, data) =>
  api.post(`/courses/${courseId}/add-material/`, data, {
    headers: {
      'Content-Type': 'multipart/form-data',  // For file uploads
    },
  });

export default api;
