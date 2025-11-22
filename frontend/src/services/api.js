import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle token refresh on 401 errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);

          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh token failed, logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API functions
export const authAPI = {
  // Sign up
  signup: async (loginId, email, password) => {
    const response = await api.post('/auth/signup/', {
      login_id: loginId,
      email: email,
      password: password,
    });
    return response.data;
  },

  // Login
  login: async (loginId, password) => {
    const response = await api.post('/auth/login/', {
      login_id: loginId,
      password: password,
    });
    return response.data;
  },

  // Request password reset OTP
  requestPasswordReset: async (email) => {
    const response = await api.post('/auth/password-reset/request/', {
      email: email,
    });
    return response.data;
  },

  // Confirm password reset with OTP
  confirmPasswordReset: async (email, otpCode, newPassword) => {
    const response = await api.post('/auth/password-reset/confirm/', {
      email: email,
      otp_code: otpCode,
      new_password: newPassword,
    });
    return response.data;
  },

  // Refresh token
  refreshToken: async (refreshToken) => {
    const response = await api.post('/auth/token/refresh/', {
      refresh: refreshToken,
    });
    return response.data;
  },
};

// Token management
export const tokenManager = {
  setTokens: (accessToken, refreshToken) => {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  },

  getAccessToken: () => {
    return localStorage.getItem('access_token');
  },

  getRefreshToken: () => {
    return localStorage.getItem('refresh_token');
  },

  clearTokens: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },
};

// Inventory API functions
export const inventoryAPI = {
  // Categories
  getCategories: async () => {
    const response = await api.get('/inventory/categories/');
    return response.data;
  },

  createCategory: async (data) => {
    const response = await api.post('/inventory/categories/', data);
    return response.data;
  },

  // Products
  getProducts: async (params = {}) => {
    const response = await api.get('/inventory/products/', { params });
    return response.data;
  },

  getProduct: async (id) => {
    const response = await api.get(`/inventory/products/${id}/`);
    return response.data;
  },

  createProduct: async (data) => {
    const response = await api.post('/inventory/products/', data);
    return response.data;
  },

  updateProduct: async (id, data) => {
    const response = await api.put(`/inventory/products/${id}/`, data);
    return response.data;
  },

  deleteProduct: async (id) => {
    const response = await api.delete(`/inventory/products/${id}/`);
    return response.data;
  },

  // Locations
  getLocations: async (params = {}) => {
    const response = await api.get('/inventory/locations/', { params });
    return response.data;
  },

  createLocation: async (data) => {
    const response = await api.post('/inventory/locations/', data);
    return response.data;
  },

  updateLocation: async (id, data) => {
    const response = await api.put(`/inventory/locations/${id}/`, data);
    return response.data;
  },

  deleteLocation: async (id) => {
    const response = await api.delete(`/inventory/locations/${id}/`);
    return response.data;
  },

  // Operation Types
  getOperationTypes: async () => {
    const response = await api.get('/inventory/operation-types/');
    return response.data;
  },

  // Pickings
  getPickings: async (params = {}) => {
    const response = await api.get('/inventory/pickings/', { params });
    return response.data;
  },

  getPicking: async (id) => {
    const response = await api.get(`/inventory/pickings/${id}/`);
    return response.data;
  },

  createPicking: async (data) => {
    const response = await api.post('/inventory/pickings/', data);
    return response.data;
  },

  updatePicking: async (id, data) => {
    const response = await api.put(`/inventory/pickings/${id}/`, data);
    return response.data;
  },

  confirmPicking: async (id) => {
    const response = await api.post(`/inventory/pickings/${id}/confirm/`);
    return response.data;
  },

  validatePicking: async (id) => {
    const response = await api.post(`/inventory/pickings/${id}/validate/`);
    return response.data;
  },

  cancelPicking: async (id) => {
    const response = await api.post(`/inventory/pickings/${id}/cancel/`);
    return response.data;
  },

  // Stock Moves
  createStockMove: async (data) => {
    const response = await api.post('/inventory/stock-moves/', data);
    return response.data;
  },

  updateStockMove: async (id, data) => {
    const response = await api.put(`/inventory/stock-moves/${id}/`, data);
    return response.data;
  },

  deleteStockMove: async (id) => {
    const response = await api.delete(`/inventory/stock-moves/${id}/`);
    return response.data;
  },

  // Stock Quantities
  getStockQuants: async (params = {}) => {
    const response = await api.get('/inventory/stock-quants/', { params });
    return response.data;
  },

  getLowStock: async () => {
    const response = await api.get('/inventory/stock-quants/low_stock/');
    return response.data;
  },

  getOutOfStock: async () => {
    const response = await api.get('/inventory/stock-quants/out_of_stock/');
    return response.data;
  },

  // Tasks
  getTasks: async (params = {}) => {
    const response = await api.get('/inventory/tasks/', { params });
    return response.data;
  },

  getMyTasks: async () => {
    const response = await api.get('/inventory/tasks/my_tasks/');
    return response.data;
  },

  completeTask: async (id) => {
    const response = await api.post(`/inventory/tasks/${id}/complete/`);
    return response.data;
  },

  // Dashboard Statistics
  getDashboardStats: async () => {
    const response = await api.get('/inventory/dashboard-stats/');
    return response.data;
  },

  // Move History
  getMoveHistory: async (params = {}) => {
    const response = await api.get('/inventory/move-history/', { params });
    return response.data;
  },

  // Warehouse Settings
  getWarehouseSettings: async () => {
    const response = await api.get('/inventory/settings/');
    return response.data;
  },

  updateWarehouseSettings: async (data) => {
    const response = await api.put('/inventory/settings/', data);
    return response.data;
  },

  partialUpdateWarehouseSettings: async (data) => {
    const response = await api.patch('/inventory/settings/', data);
    return response.data;
  },
};

export default api;
