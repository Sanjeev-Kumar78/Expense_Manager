import axios, { AxiosResponse } from 'axios';
import { User, Expense, Transaction, SpendingSummary, RegisterData, LoginData } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, logout user
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  register: async (userData: RegisterData): Promise<{ user: User; access_token: string }> => {
    const response: AxiosResponse = await api.post('/users/register', userData);
    return response.data;
  },

  login: async (loginData: LoginData): Promise<{ user: User; access_token: string }> => {
    const response: AxiosResponse = await api.post('/users/login', loginData);
    return response.data;
  },

  getProfile: async (): Promise<User> => {
    const response: AxiosResponse = await api.get('/users/profile');
    return response.data;
  },

  updateProfile: async (userData: Partial<User>): Promise<User> => {
    const response: AxiosResponse = await api.put('/users/profile', userData);
    return response.data;
  },
};

// Expense API calls
export const expenseAPI = {
  getExpenses: async (): Promise<Expense[]> => {
    const response: AxiosResponse = await api.get('/expenses');
    return response.data;
  },

  createExpense: async (expenseData: Omit<Expense, 'id' | 'user_id' | 'created_at'>): Promise<Expense> => {
    const response: AxiosResponse = await api.post('/expenses', expenseData);
    return response.data;
  },

  updateExpense: async (id: string, expenseData: Partial<Expense>): Promise<Expense> => {
    const response: AxiosResponse = await api.put(`/expenses/${id}`, expenseData);
    return response.data;
  },

  deleteExpense: async (id: string): Promise<void> => {
    await api.delete(`/expenses/${id}`);
  },

  uploadReceipt: async (file: File): Promise<Expense> => {
    const formData = new FormData();
    formData.append('file', file);
    const response: AxiosResponse = await api.post('/expenses/receipt', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// Transaction API calls
export const transactionAPI = {
  getTransactions: async (): Promise<Transaction[]> => {
    const response: AxiosResponse = await api.get('/transactions');
    return response.data;
  },

  createTransaction: async (transactionData: Omit<Transaction, 'id' | 'user_id' | 'created_at'>): Promise<Transaction> => {
    const response: AxiosResponse = await api.post('/transactions', transactionData);
    return response.data;
  },
};

// Summary API calls
export const summaryAPI = {
  getSpendingSummary: async (): Promise<SpendingSummary> => {
    const response: AxiosResponse = await api.get('/summary/spending');
    return response.data;
  },

  getCategorySummary: async (): Promise<{ [key: string]: number }> => {
    const response: AxiosResponse = await api.get('/summary/categories');
    return response.data;
  },

  getTrends: async (): Promise<any> => {
    const response: AxiosResponse = await api.get('/summary/trends');
    return response.data;
  },

  chatWithAI: async (message: string): Promise<{ response: string }> => {
    const response: AxiosResponse = await api.post('/summary/chat', { message });
    return response.data;
  },
};

export default api;