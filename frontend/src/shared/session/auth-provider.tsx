'use client'

import React, { useEffect, useState } from "react";
import { createContext, useContext } from "react";

import { AccessTokenPayload } from "./access-token-payload";
import { sessionStorage } from "./session-store";
import { ERROR_MESSAGE } from "../constants/errors";

interface AuthContextType {
  user: AccessTokenPayload | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  setSession: (accessToken: string) => void;
  clearSession: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<AccessTokenPayload | null>(null)
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const savedUser = sessionStorage.getUserData();
    if(savedUser) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setUser(savedUser);
    }
    setIsLoading(false)
  }, [])

  const setSession = (accessToken: string) => {
    sessionStorage.setSession(accessToken);
    setUser(sessionStorage.getUserData());
  }

  const clearSession = () => {
    sessionStorage.clearSession();
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: user ? true : false,
        setSession,
        clearSession,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error(ERROR_MESSAGE.SessionContextError);
  }
  return context;
}