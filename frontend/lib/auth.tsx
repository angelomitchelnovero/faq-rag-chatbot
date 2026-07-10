"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import * as api from "./api";

interface AuthContextValue {
  user: api.User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<api.User>;
  register: (
    email: string,
    password: string,
    adminSignupCode?: string
  ) => Promise<api.User>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<api.User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .getMe()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("access_token");
      })
      .finally(() => setLoading(false));
  }, []);

  async function login(email: string, password: string) {
    const res = await api.login(email, password);
    localStorage.setItem("access_token", res.access_token);
    setUser(res.user);
    return res.user;
  }

  async function register(
    email: string,
    password: string,
    adminSignupCode?: string
  ) {
    const res = await api.register(email, password, adminSignupCode);
    localStorage.setItem("access_token", res.access_token);
    setUser(res.user);
    return res.user;
  }

  function logout() {
    localStorage.removeItem("access_token");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
