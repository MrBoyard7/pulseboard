/* eslint-disable react-refresh/only-export-components -- this file intentionally
   pairs the AuthProvider component with its companion useAuth hook, a standard
   React context pattern that the fast-refresh rule otherwise flags. */
import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { apiClient, clearStoredToken, getStoredToken, setStoredToken } from "@/api/client";
import type { User } from "@/types";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      setIsLoading(false);
      return;
    }
    apiClient
      .get<User>("/api/auth/me")
      .then((response) => setUser(response.data))
      .catch(() => clearStoredToken())
      .finally(() => setIsLoading(false));
  }, []);

  const login = async (email: string, password: string) => {
    const response = await apiClient.post<{ access_token: string }>("/api/auth/login", {
      email,
      password,
    });
    setStoredToken(response.data.access_token);
    const me = await apiClient.get<User>("/api/auth/me");
    setUser(me.data);
  };

  const logout = () => {
    clearStoredToken();
    setUser(null);
  };

  const value = useMemo(() => ({ user, isLoading, login, logout }), [user, isLoading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}