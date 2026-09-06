import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { fetchCurrentUser, login as apiLogin, signup as apiSignup, type UserResponse } from "../api/auth";
import { setAuthToken } from "../api/client";

const TOKEN_STORAGE_KEY = "calorie_tracker_token";

interface AuthContextValue {
  user: UserResponse | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (!token) {
      setIsLoading(false);
      return;
    }
    setAuthToken(token);
    fetchCurrentUser()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem(TOKEN_STORAGE_KEY);
        setAuthToken(null);
      })
      .finally(() => setIsLoading(false));
  }, []);

  async function handleAuthSuccess(token: string) {
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
    setAuthToken(token);
    const currentUser = await fetchCurrentUser();
    setUser(currentUser);
  }

  async function login(email: string, password: string) {
    const { access_token } = await apiLogin(email, password);
    await handleAuthSuccess(access_token);
  }

  async function signup(email: string, password: string) {
    const { access_token } = await apiSignup(email, password);
    await handleAuthSuccess(access_token);
  }

  function logout() {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setAuthToken(null);
    setUser(null);
  }

  const value = useMemo(() => ({ user, isLoading, login, signup, logout }), [user, isLoading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
}
