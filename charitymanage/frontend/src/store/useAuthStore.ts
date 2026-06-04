import { create } from 'zustand';
import api from '../api';

interface User {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  is_superuser: boolean;
  groups: {id: number, name: string}[];
}

interface AuthStore {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
  fetchUser: () => Promise<void>;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: localStorage.getItem('access_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  login: (token: string) => {
    localStorage.setItem('access_token', token);
    set({ token, isAuthenticated: true });
  },
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ token: null, isAuthenticated: false, user: null });
  },
  fetchUser: async () => {
    try {
      const res = await api.get('/api/users/me/');
      set({ user: res.data });
    } catch (e) {
      console.error(e);
      // Logout on fail
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      set({ token: null, isAuthenticated: false, user: null });
    }
  }
}));

// Setup Axios interceptor to append JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
