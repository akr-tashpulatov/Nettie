import { ERROR_MESSAGE } from "@/shared/constants/errors";
import {
  AccessTokenPayload,
  accessTokenPayloadSchema,
  decodeAccessToken,
} from "./access-token-payload";

const USER_DATA_KEY = 'user-data'

const safeStorage = {
  getItem: (key: string): string | null => {
    try {
      if (typeof window === 'undefined') return null;
      const value = localStorage.getItem(key);
      return value;
    } catch (error) {
      console.error(ERROR_MESSAGE.TokenError, error);
      return null;
    }
  },
  setItem: (key: string, value: string): boolean => {
    try {
      if (typeof window === 'undefined') return false;
      localStorage.setItem(key, value);
      return true;
    } catch (error) {
      console.error(ERROR_MESSAGE.TokenError, error);
      return false;
    }
  },
  removeItem: (key: string): boolean => {
    try {
      if (typeof window === 'undefined') return false;
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error(ERROR_MESSAGE.TokenError, error);
      return false;
    }
  },
};


class SessionStore {
  setSession(accessToken: string) {
    const payload = decodeAccessToken(accessToken);
    if (!payload) {
      console.error(ERROR_MESSAGE.TokenError);
      return;
    }
    safeStorage.setItem(USER_DATA_KEY, JSON.stringify(payload));
  }

  getUserData(): AccessTokenPayload | null {
    const userData = safeStorage.getItem(USER_DATA_KEY);
    if (!userData) return null;
    try {
      const result = accessTokenPayloadSchema.safeParse(JSON.parse(userData));
      if (result.success) return result.data;
    } catch {
      // fall through: corrupted storage is treated as no session
    }
    safeStorage.removeItem(USER_DATA_KEY);
    return null;
  }

  clearSession() {
    safeStorage.removeItem(USER_DATA_KEY);
  }
}

export const sessionStorage = new SessionStore()
