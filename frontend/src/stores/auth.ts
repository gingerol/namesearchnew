import { create } from "zustand";

export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_superuser?: boolean;
  [key: string]: unknown;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (credentials: { email: string; password: string }) => Promise<void>;
  logout: () => void;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
}

export const useAuthStore = create<AuthState>((set: (state: Partial<AuthState>) => void) => ({
  user: null,
  token: localStorage.getItem("auth_token"),
  isLoading: false,

  login: async (credentials: { email: string; password: string }) => {
    set({ isLoading: true });
    // TODO: Replace with real API call
    try {
      // Example: const { user, token } = await api.login(credentials)
      const user: User = { id: 1, email: credentials.email, is_superuser: true };
      const token: string = "dummy-token";
      localStorage.setItem("auth_token", token);
      set({ user, token, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem("auth_token");
    set({ user: null, token: null });
  },

  setUser: (user: User | null) => set({ user }),
  setToken: (token: string | null) => set({ token }),
}));
