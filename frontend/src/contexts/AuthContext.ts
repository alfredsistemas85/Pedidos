import { create } from 'zustand';

interface AuthState {
  token: string | null;
  role: string | null;
  isAuthenticated: boolean;
  setAuth: (token: string, role: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => {
  const token = localStorage.getItem('access_token');
  const role = localStorage.getItem('user_role');

  return {
    token,
    role,
    isAuthenticated: !!token,
    setAuth: (token, role) => {
      localStorage.setItem('access_token', token);
      localStorage.setItem('user_role', role);
      set({ token, role, isAuthenticated: true });
    },
    logout: () => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_role');
      set({ token: null, role: null, isAuthenticated: false });
    },
  };
});
